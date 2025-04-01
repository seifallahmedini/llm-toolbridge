"""
Azure OpenAI Provider module.

This module provides the implementation of the Provider interface for Azure OpenAI.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from openai import AzureOpenAI
from pydantic import BaseModel, Field

from src.core.provider import Provider, ProviderConfig, LLMResponse, ToolCall
from src.core.tool import Tool


logger = logging.getLogger(__name__)


class AzureOpenAIConfig(ProviderConfig):
    """
    Configuration for Azure OpenAI provider.
    
    Args:
        api_key: The API key for Azure OpenAI.
        endpoint: The Azure OpenAI endpoint URL.
        deployment_name: The name of the deployment to use.
        api_version: The API version to use.
        organization: Optional organization for the API key.
    """
    api_key: str
    endpoint: str
    deployment_name: str
    api_version: str = "2023-12-01-preview"
    organization: Optional[str] = None


class AzureOpenAIProvider(Provider):
    """
    Implementation of the Provider interface for Azure OpenAI.
    
    This provider allows interaction with Azure OpenAI API for LLM generation
    with tool calling capabilities.
    """
    
    def __init__(self, config: AzureOpenAIConfig):
        """
        Initialize the Azure OpenAI provider.
        
        Args:
            config: The configuration for the Azure OpenAI provider.
        """
        self.config = config
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint,
            organization=config.organization
        )
        self.deployment_name = config.deployment_name
    
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from Azure OpenAI.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional parameters for the Azure OpenAI API.
            
        Returns:
            The LLM's response.
            
        Raises:
            Exception: If there's an error calling the Azure OpenAI API.
        """
        # Synchronous implementation for now (we'll add proper async later)
        return self._generate_sync(prompt, tools, tool_results, **kwargs)
    
    def _generate_sync(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Synchronous implementation of generate.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional parameters for the Azure OpenAI API.
            
        Returns:
            The LLM's response.
            
        Raises:
            Exception: If there's an error calling the Azure OpenAI API.
        """
        messages = [{"role": "user", "content": prompt}]
        
        # Add tool results as tool messages if available
        if tool_results:
            for tool_id, result in tool_results.items():
                # Add result as tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": json.dumps(result)
                })
        
        # Prepare request parameters
        request_params = {
            "model": self.deployment_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 800),
            "top_p": kwargs.get("top_p", 1.0)
        }
        
        # Add tools if provided
        if tools:
            formatted_tools = self.format_tools_for_provider(tools)
            request_params["tools"] = formatted_tools
            # Only add tool_choice if tools are provided
            request_params["tool_choice"] = kwargs.get("tool_choice", "auto")
        
        try:
            # Make the API call using the client
            response = self.client.chat.completions.create(**request_params)
            
            # Parse the response
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {e}")
            raise Exception(f"Azure OpenAI API request failed: {str(e)}")
    
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Format the tools for the Azure OpenAI API.
        
        Args:
            tools: The tools to format.
            
        Returns:
            The tools formatted for Azure OpenAI.
        """
        formatted_tools = []
        
        for tool in tools:
            # Leverage the to_dict method from the Tool class
            tool_dict = {
                "type": "function",
                "function": tool.to_dict()
            }
            
            # The to_dict method already handles parameter formatting correctly,
            # including handling both dict and ParameterDefinition objects
            formatted_tools.append(tool_dict)
        
        return formatted_tools
    
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        """
        Parse tool calls from the Azure OpenAI API response.
        
        This method extracts tool calls from the raw API response and converts
        them into our standardized ToolCall format. It handles the Azure OpenAI
        specific response structure and error cases.
        
        Args:
            raw_response: The raw response from the OpenAI client.
            
        Returns:
            List[ToolCall]: A list of parsed tool calls ready for execution.
            
        Raises:
            No explicit exceptions, but logs errors that occur during parsing.
        """
        tool_calls = []
        
        try:
            # Extract choices from the response object
            choices = raw_response.choices if hasattr(raw_response, 'choices') else []
            
            for choice in choices:
                # Get message from the choice
                message = choice.message if hasattr(choice, 'message') else None
                
                # Get tool_calls from the message
                raw_tool_calls = message.tool_calls if message and hasattr(message, 'tool_calls') else []
                
                for raw_call in raw_tool_calls:
                    if hasattr(raw_call, 'type') and raw_call.type == "function":
                        # Extract function details
                        function_data = raw_call.function
                        
                        # Parse arguments as JSON
                        arguments = {}
                        try:
                            arguments_str = function_data.arguments
                            arguments = json.loads(arguments_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing tool call arguments: {e}")
                            arguments = {"error": "Invalid JSON in arguments"}
                        
                        tool_call = ToolCall(
                            tool_name=function_data.name,
                            arguments=arguments,
                            call_id=raw_call.id
                        )
                        
                        tool_calls.append(tool_call)
        
        except Exception as e:
            logger.error(f"Error parsing tool calls: {e}")
        
        return tool_calls
    
    def _parse_response(self, response: Any) -> LLMResponse:
        """
        Parse the response from Azure OpenAI API into our standard LLMResponse format.
        
        This method handles the extraction of both text content and tool calls
        from the Azure OpenAI API response. It creates a structured LLMResponse
        object that standardizes how we interact with the LLM output across
        different providers.
        
        Args:
            response: The response object from the OpenAI client.
            
        Returns:
            LLMResponse: A structured object containing the LLM's text response
                         and/or tool calls.
            
        Raises:
            No explicit exceptions, but handles errors internally and returns
            an error message in the LLMResponse content if parsing fails.
        """
        try:
            # Check if we have choices in the response
            if not hasattr(response, 'choices') or not response.choices:
                return LLMResponse(content="No response generated")
            
            # Get the first choice
            choice = response.choices[0]
            
            # Get the message from the choice
            message = choice.message if hasattr(choice, 'message') else None
            
            # Extract content
            content = message.content if message and hasattr(message, 'content') else None
            
            # Parse tool calls
            tool_calls = self.parse_tool_calls(response)
            
            return LLMResponse(
                content=content,
                tool_calls=tool_calls
            )
            
        except Exception as e:
            logger.error(f"Error parsing Azure OpenAI response: {e}")
            return LLMResponse(content=f"Error parsing response: {str(e)}")