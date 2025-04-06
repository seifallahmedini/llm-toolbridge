"""
Google Gemini Provider module.

This module implements the Provider interface for Google's Gemini AI models,
enabling the use of function calling capabilities.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union, cast, Literal
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from ..core.provider import Provider, ProviderConfig, LLMResponse, ToolCall
from ..core.tool import Tool

# Configure logging
logger = logging.getLogger(__name__)


class GeminiConfig(ProviderConfig):
    """
    Configuration for the Google Gemini provider.

    Args:
        api_key: Google AI API key.
        model: The Gemini model to use (e.g., "gemini-2.0-pro").
        function_calling_mode: Controls how the model uses the provided functions.
                             Options: "AUTO" (default), "ANY", "NONE".
        generation_config: Optional configuration for generation parameters.
    """
    api_key: str
    model: str = "gemini-2.0-pro"
    function_calling_mode: Literal["AUTO", "ANY", "NONE"] = "AUTO"
    generation_config: Optional[Dict[str, Any]] = None


class GeminiProvider(Provider):
    """
    Provider implementation for Google's Gemini AI models.
    
    This provider interfaces with Google's Gemini models and supports
    function calling capabilities through the Google Gen AI SDK.
    """
    
    def __init__(self, config: GeminiConfig):
        """
        Initialize the Gemini provider.
        
        Args:
            config: Configuration for the Gemini provider.
        """
        self.config = config
        self.model_name = config.model
        
        # Initialize the Google Generative AI client
        self.client = genai.Client(api_key=config.api_key)
        
        # Set up generation config
        self.gen_config = config.generation_config or {}
    
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the Gemini model.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The LLM's response.
        """
        try:
            # Convert to synchronous call using asyncio.to_thread 
            # (Google Generative AI SDK is primarily synchronous)
            return await asyncio.to_thread(
                self._generate_sync, 
                prompt=prompt,
                tools=tools,
                tool_results=tool_results,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error generating response from Gemini: {str(e)}")
            raise RuntimeError(f"Gemini API error: {str(e)}") from e
            
    def _generate_sync(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Synchronous version of generate method.
        
        Args:
            prompt: The prompt to send to Gemini.
            tools: Optional list of tools to make available.
            tool_results: Optional results from previously called tools.
            **kwargs: Additional parameters.
            
        Returns:
            LLMResponse object with content and/or tool calls.
        """
        generation_config = {**self.gen_config, **kwargs.get("generation_config", {})}
        
        # Prepare the contents for the request using the proper types.Content structure
        if tool_results:
            # Create a conversation history using types.Content objects
            contents = [
                # Original user prompt as the first message
                types.Content(
                    role="user", 
                    parts=[types.Part(text=prompt)]
                )
            ]
            
            # For each tool result, add a model function call followed by user function response
            for tool_id, result_data in tool_results.items():
                # Extract the base tool name (without the ID suffix)
                tool_name = tool_id.split("-")[0] if "-" in tool_id else tool_id
                
                # Add a synthetic model response that issued the function call
                # This maintains conversation consistency even though we may not have the original call
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part(function_call=types.FunctionCall(name=tool_name, args={}))]
                    )
                )
                
                # Add the user's function response with the result
                if result_data:
                    # Wrap the result value in a dict if it's not already a dict or list
                    response_data = result_data
                    if not isinstance(response_data, dict) and not isinstance(response_data, list):
                        response_data = {"result": response_data}
                        
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_function_response(
                                    name=tool_name,
                                    response=response_data
                                )
                            ]
                        )
                    )
                else:
                    # Handle error responses
                    error_msg = result_data.get("error", "Unknown error")
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_function_response(
                                    name=tool_name,
                                    response={"error": error_msg}
                                )
                            ]
                        )
                    )
        else:
            # If no tool results, just use a simple content structure
            contents = [
                types.Content(
                    role="user", 
                    parts=[types.Part(text=prompt)]
                )
            ]
        
        try:
            # Create the request parameters
            request_params = {
                "model": self.model_name,
                "contents": contents,
            }
            
            # Configure tools and function calling if provided
            if tools:
                gemini_tool = self.format_tools_for_provider(tools)
                
                # Create proper GenerateContentConfig with function calling configuration
                config = types.GenerateContentConfig(
                    tools=[gemini_tool],
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode=self.config.function_calling_mode
                        )
                    )
                )
                request_params["config"] = config
            
            # Add any additional generation parameters if needed
            if generation_config:
                # If we don't have a config already, create one
                if "config" not in request_params:
                    request_params["config"] = types.GenerateContentConfig(**generation_config)
                else:
                    # Otherwise update the existing config with additional parameters
                    for key, value in generation_config.items():
                        if hasattr(request_params["config"], key):
                            setattr(request_params["config"], key, value)
                
            # Send the request to Gemini
            response = self.client.models.generate_content(**request_params)
            
            # Parse the response
            response_text = response.text if hasattr(response, "text") else ""
            tool_calls = []
            if response.function_calls is not None:
                tool_calls = self.parse_tool_calls(response)
            
            return LLMResponse(
                content=response_text,
                tool_calls=tool_calls
            )
            
        except Exception as e:
            logger.error(f"Error in Gemini API call: {str(e)}")
            raise RuntimeError(f"Gemini API error: {str(e)}") from e
    
    def format_tools_for_provider(self, tools: List[Tool]) -> Any:
        """
        Format tools in the format expected by Google Gemini.
        
        Args:
            tools: List of tools to format.
            
        Returns:
            Properly formatted tools object for Gemini API.
        """
        # Create function declarations list for the Gemini types.Tool constructor
        function_declarations = []
        
        for tool in tools:
            # Convert our tool schema to Gemini's function declaration format
            schema = tool.to_dict()
            
            # Create the function declaration dict
            function_declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add parameters from the tool schema with modifications for Gemini API compatibility
            if "parameters" in schema and "properties" in schema["parameters"]:
                # Process each parameter to ensure compatibility with Gemini API
                for param_name, param_def in schema["parameters"]["properties"].items():
                    # Create a clean copy of the parameter definition
                    clean_param = param_def.copy() if isinstance(param_def, dict) else param_def
                    
                    # Remove default value if present as Gemini API doesn't support it
                    if isinstance(clean_param, dict) and "default" in clean_param:
                        del clean_param["default"]
                    
                    # Add the cleaned parameter to the function declaration
                    function_declaration["parameters"]["properties"][param_name] = clean_param
                
                # Add required parameters
                if "required" in schema["parameters"]:
                    function_declaration["parameters"]["required"] = schema["parameters"]["required"]
            
            function_declarations.append(function_declaration)
        
        # Create a Gemini Tool object using function_declarations
        gemini_tool = types.Tool(function_declarations=function_declarations)
        return gemini_tool
    
    def parse_tool_calls(self, response: Any) -> List[ToolCall]:
        """
        Parse tool calls from the Gemini response.
        
        Args:
            response: The raw response from Gemini.
            
        Returns:
            List of standardized ToolCall objects.
        """
        tool_calls = []
        
        try:
            # Check for direct function_call property on response
            if hasattr(response, "function_call"):
                function_call = response.function_call
                try:
                    # Handle args as dict or string
                    if isinstance(function_call.args, dict):
                        arguments = function_call.args
                    else:
                        arguments = json.loads(function_call.args)
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.debug(f"Error parsing direct function call args: {e}")
                    arguments = {"raw_args": str(function_call.args)}
                
                tool_calls.append(
                    ToolCall(
                        tool_name=function_call.name,
                        arguments=arguments,
                        call_id="gemini-direct-call"
                    )
                )
            
            # Check for function_calls array property on response
            if hasattr(response, "function_calls"):
                for idx, func_call in enumerate(response.function_calls):
                    try:
                        # Handle args as dict, string, or serialized object
                        if isinstance(func_call.args, dict):
                            arguments = func_call.args
                        elif hasattr(func_call.args, "__dict__"):
                            # If it's an object with attributes
                            arguments = vars(func_call.args)
                        else:
                            # Try to parse as JSON string
                            arguments = json.loads(str(func_call.args))
                    except (json.JSONDecodeError, AttributeError, TypeError) as e:
                        logger.debug(f"Error parsing function_calls args: {e}")
                        # Fall back to passing the raw string or repr
                        arguments = {"raw_args": repr(func_call.args)}
                    
                    tool_calls.append(
                        ToolCall(
                            tool_name=func_call.name,
                            arguments=arguments,
                            call_id=f"gemini-function-{idx}"
                        )
                    )
            
            # Check for parts directly on the response
            if hasattr(response, "parts"):
                for part_idx, part in enumerate(response.parts):
                    if hasattr(part, "function_call"):
                        function_call = part.function_call
                        try:
                            arguments = (
                                function_call.args
                                if isinstance(function_call.args, dict)
                                else json.loads(function_call.args)
                            )
                        except (json.JSONDecodeError, AttributeError):
                            arguments = {"raw_args": str(function_call.args)}
                        
                        tool_calls.append(
                            ToolCall(
                                tool_name=function_call.name,
                                arguments=arguments,
                                call_id=f"gemini-part-{part_idx}"
                            )
                        )
            
            # Handle special case for non-text parts warning
            if not tool_calls and hasattr(response, "text"):
                warning_text = response.text if response.text else ""
                if "non-text parts in the response: ['function_call']" in warning_text:
                    logger.debug("Detected non-text parts warning, checking candidates manually")
                    try:
                        # Try to extract function calls directly from candidates
                        if hasattr(response, "_candidate_dict") and response._candidate_dict:
                            candidate_dict = response._candidate_dict
                            if "content" in candidate_dict and "parts" in candidate_dict["content"]:
                                for part_idx, part in enumerate(candidate_dict["content"]["parts"]):
                                    if "function_call" in part:
                                        func_call = part["function_call"]
                                        tool_calls.append(
                                            ToolCall(
                                                tool_name=func_call.get("name", "unknown"),
                                                arguments=func_call.get("args", {}),
                                                call_id=f"gemini-manual-{part_idx}"
                                            )
                                        )
                    except Exception as extract_err:
                        logger.debug(f"Error extracting function calls from candidate dict: {extract_err}")
                    
        except Exception as e:
            logger.warning(f"Error parsing tool calls: {str(e)}")
            logger.debug(f"Response structure: {dir(response)}")
        
        return tool_calls