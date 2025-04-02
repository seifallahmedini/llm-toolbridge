"""
Provider package.

This package contains provider implementations for various LLM services.
"""

# Register all adapters in the registry
from src.core.adapter_registry import AdapterRegistry

# Import providers and adapters
from src.providers.azure_openai import AzureOpenAIProvider
from src.providers.openai import OpenAIProvider

# Import and register provider adapters
try:
    from src.providers.openai_adapter import OpenAIAdapter
    AdapterRegistry.register("openai", OpenAIAdapter)
except ImportError:
    pass  # Skip if not available

# Register other adapters as they become available
try:
    # Placeholder for future adapter imports
    pass
except ImportError:
    pass