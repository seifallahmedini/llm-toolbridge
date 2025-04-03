"""
LLM Tool Bridge package.

A unified interface for working with tool calling across different LLM providers.
"""

# Import core components for easy access
from .core.bridge import ToolBridge
from .core.tool import Tool
from .core.adapter import BaseProviderAdapter, ProviderCapabilities
from .core.provider import Provider, LLMResponse, ToolCall
from .core.adapter_registry import AdapterRegistry

# Import adapters package to ensure registration
from .adapters.azure_openai import AzureOpenAIAdapter
from .adapters.openai import OpenAIAdapter