"""
Provider interface module.

This module defines the base Provider interface and related types that
all LLM provider implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from .tool import Tool


class ProviderConfig(BaseModel):
    """Base configuration for all providers."""
    pass


class ToolCall(BaseModel):
    """
    Represents a tool call from an LLM.

    Args:
        tool_name: The name of the tool to call.
        arguments: The arguments to pass to the tool.
        call_id: A unique identifier for this tool call.
    """
    tool_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None


class LLMResponse(BaseModel):
    """
    Represents a response from an LLM.

    Args:
        content: The text response from the LLM.
        tool_calls: Any tool calls requested by the LLM.
    """
    content: Optional[str] = None
    tool_calls: List[ToolCall] = []


class Provider(ABC):
    """
    Base interface for all LLM providers.
    
    All LLM provider implementations must inherit from this class
    and implement its abstract methods.
    """
    
    @abstractmethod
    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider with the given configuration.
        
        Args:
            config: Provider-specific configuration.
        """
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The LLM's response.
        """
        pass
    
    @abstractmethod
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Format the tools in a way that the provider understands.
        
        Args:
            tools: The tools to format.
            
        Returns:
            The tools formatted for the specific provider.
        """
        pass
    
    @abstractmethod
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        """
        Parse tool calls from the raw provider response.
        
        Args:
            raw_response: The raw response from the provider.
            
        Returns:
            A list of parsed tool calls.
        """
        pass