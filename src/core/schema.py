"""
Schema module.

This module provides the common schema classes for request and response
formats used throughout the LLM Tool Bridge library.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from src.core.tool import Tool


class ToolBridgeRequest(BaseModel):
    """
    Base class for tool bridge requests.
    
    Args:
        prompt: The prompt to send to the LLM.
        tools: Optional list of tools to make available to the LLM.
        model: Optional model identifier to use for generation.
        temperature: Optional temperature parameter for generation.
        max_tokens: Optional maximum number of tokens to generate.
    """
    prompt: str
    tools: Optional[List[Tool]] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True


class ToolResult(BaseModel):
    """
    Result of a tool execution.
    
    Args:
        tool_name: The name of the tool that was called.
        call_id: A unique identifier for the tool call.
        result: The result of the tool execution.
        error: Optional error message if the tool execution failed.
        success: Whether the tool execution was successful.
    """
    tool_name: str
    call_id: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    success: bool = True


class ToolBridgeResponse(BaseModel):
    """
    Response from the tool bridge.
    
    Args:
        content: The text response from the LLM.
        tool_results: Results of any tool calls that were made.
        provider_name: The name of the provider that generated the response.
        usage: Optional usage statistics from the provider.
    """
    content: Optional[str] = None
    tool_results: List[ToolResult] = Field(default_factory=list)
    provider_name: str
    usage: Optional[Dict[str, Any]] = None