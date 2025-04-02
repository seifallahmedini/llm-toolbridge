"""
Provider Adapter interface module.

This module defines the adapter pattern that serves as an abstraction layer
between the ToolBridge and specific LLM provider implementations, providing
a unified tool calling API regardless of the underlying LLM service.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic

from pydantic import BaseModel

from src.core.provider import Provider, ProviderConfig, LLMResponse, ToolCall
from src.core.tool import Tool


# Type variables for generic typing
T = TypeVar('T')  # For provider-specific request
R = TypeVar('R')  # For provider-specific response


class ProviderCapabilities(BaseModel):
    """
    Defines the capabilities of an LLM provider.
    
    Args:
        supports_tool_calling: Whether the provider supports tool/function calling
        supports_multiple_tools: Whether multiple tools can be used in a single request
        supports_streaming: Whether streaming responses are supported
        supports_vision: Whether vision/image inputs are supported
        max_tokens_limit: Maximum number of tokens supported in a request
    """
    supports_tool_calling: bool = False
    supports_multiple_tools: bool = False
    supports_streaming: bool = False
    supports_vision: bool = False
    max_tokens_limit: Optional[int] = None
    

class BaseProviderAdapter(Generic[T, R], ABC):
    """
    Base adapter interface for LLM providers.
    
    This adapter serves as an abstraction layer between the ToolBridge and
    specific provider implementations, translating between our standard API
    and provider-specific APIs.
    """
    
    @abstractmethod
    def __init__(self, provider: Provider):
        """
        Initialize the adapter with a provider.
        
        Args:
            provider: The underlying provider implementation.
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """
        Get the capabilities of this provider.
        
        Returns:
            A ProviderCapabilities object describing what the provider can do.
        """
        pass
    
    @abstractmethod
    def prepare_request(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> T:
        """
        Prepare a provider-specific request object.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional parameters for the request.
            
        Returns:
            A provider-specific request object.
        """
        pass
    
    @abstractmethod
    def execute_request(self, request: T) -> R:
        """
        Execute a prepared request using the provider.
        
        Args:
            request: The provider-specific request to execute.
            
        Returns:
            A provider-specific response object.
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: R) -> LLMResponse:
        """
        Parse a provider-specific response into our standard format.
        
        Args:
            response: The provider-specific response to parse.
            
        Returns:
            A standardized LLMResponse object.
        """
        pass
    
    def process_tool_call(
        self,
        tool_call: ToolCall,
        registered_tools: Dict[str, Tool]
    ) -> Dict[str, Any]:
        """
        Process a tool call using the registered tools.
        
        Args:
            tool_call: The tool call to process.
            registered_tools: Dictionary of registered tools.
            
        Returns:
            The result of executing the tool call.
            
        Raises:
            KeyError: If the requested tool isn't registered.
            Exception: If tool execution fails.
        """
        try:
            tool = registered_tools[tool_call.tool_name]
            return {
                "result": tool.invoke(tool_call.arguments),
                "success": True
            }
        except KeyError:
            return {
                "error": f"Tool '{tool_call.tool_name}' not found",
                "success": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
            
    def execute_with_tools(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        max_tool_calls: int = 10,
        **kwargs
    ) -> LLMResponse:
        """
        Execute the LLM with tools, handling the complete conversation flow.
        
        This method orchestrates the conversation including any tool calls,
        maintaining a standardized flow regardless of provider implementation.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            max_tool_calls: Maximum number of tool calls to allow (prevents infinite loops).
            **kwargs: Additional parameters for the LLM.
            
        Returns:
            The final LLM response after processing all tool calls.
            
        Raises:
            ValueError: If max_tool_calls is less than 1.
            RuntimeError: If tool processing fails unexpectedly.
        """
        if max_tool_calls < 1:
            raise ValueError("max_tool_calls must be at least 1")
            
        tools_dict = {tool.name: tool for tool in (tools or [])}
        tool_results = {}
        
        try:
            # Prepare and execute initial request with tools
            request = self.prepare_request(prompt, tools, **kwargs)
            response_obj = self.execute_request(request)
            llm_response = self.parse_response(response_obj)
            
            # Process tool calls if present
            if llm_response.tool_calls:
                # Track processed tool calls for debugging
                processed_tools = []
                
                # Process all tool calls from the response
                for tool_call in llm_response.tool_calls[:max_tool_calls]:
                    result = self.process_tool_call(tool_call, tools_dict)
                    call_id = tool_call.call_id or tool_call.tool_name
                    tool_results[call_id] = result
                    processed_tools.append(tool_call.tool_name)
                
                # Send follow-up request with tool results (without tools to avoid API errors)
                if tool_results:
                    request = self.prepare_request(prompt, None, tool_results, **kwargs)
                    response_obj = self.execute_request(request)
                    llm_response = self.parse_response(response_obj)
            
            return llm_response
            
        except Exception as e:
            # Add context to any exceptions
            raise RuntimeError(f"Tool execution failed: {str(e)}") from e