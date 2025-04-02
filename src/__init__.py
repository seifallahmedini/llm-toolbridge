"""
LLM Tool Bridge package.

A unified interface for working with tool calling across different LLM providers.
"""

# Import core components for easy access
from src.core.bridge import ToolBridge
from src.core.tool import Tool
from src.core.adapter import BaseProviderAdapter, ProviderCapabilities
from src.core.provider import Provider, LLMResponse, ToolCall
from src.core.adapter_registry import AdapterRegistry

# Import adapters package to ensure registration
import src.adapters