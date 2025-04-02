"""
Adapters package.

This package contains adapter implementations for various LLM providers.
Adapters serve as a bridge between the generic Tool Bridge interface and
specific provider implementations.
"""

from src.core.adapter_registry import AdapterRegistry

# Import and register provider adapters
try:
    from src.adapters.openai import OpenAIAdapter
    AdapterRegistry.register("openai", OpenAIAdapter)
except ImportError:
    pass  # Skip if not available

try:
    from src.adapters.azure_openai import AzureOpenAIAdapter
    AdapterRegistry.register("azure_openai", AzureOpenAIAdapter)
except ImportError:
    pass  # Skip if not available