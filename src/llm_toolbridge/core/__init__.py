"""
Core package for LLM Tool Bridge.

This module provides the core classes and interfaces for working with
tools across different LLM providers.
"""

from .bridge import ToolBridge
from .provider import Provider, ProviderConfig, ToolCall, LLMResponse
from .tool import Tool, ParameterDefinition

__all__ = [
    'ToolBridge',
    'Provider',
    'ProviderConfig',
    'ToolCall',
    'LLMResponse',
    'Tool',
    'ParameterDefinition',
]