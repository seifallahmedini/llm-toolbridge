"""
Core package for LLM Tool Bridge.

This module provides the core classes and interfaces for working with
tools across different LLM providers.
"""

from src.core.bridge import ToolBridge
from src.core.provider import Provider, ProviderConfig, ToolCall, LLMResponse
from src.core.tool import Tool, ParameterDefinition

__all__ = [
    'ToolBridge',
    'Provider',
    'ProviderConfig',
    'ToolCall',
    'LLMResponse',
    'Tool',
    'ParameterDefinition',
]