# Provider Adapters

This section documents the provider adapters in the LLM Tool Bridge library. Adapters provide a standardized way to use different LLM providers through a common interface.

## Overview

Provider adapters serve as an abstraction layer between the `ToolBridge` and specific provider implementations. They enable:

1. **Provider-agnostic code**: Write code once and seamlessly switch between providers
2. **Capability inspection**: Query provider capabilities before making requests
3. **Standardized error handling**: Consistent error handling across different providers
4. **Easy provider switching**: Swap out providers without changing your application code

## Adapter Architecture

Each adapter:
- Wraps a specific provider implementation
- Translates between the standard ToolBridge interface and provider-specific details
- Reports provider capabilities
- Handles request preparation and response parsing

## Available Adapters

- [Azure OpenAI Adapter](./azure_openai.md) - Adapter for Azure-hosted OpenAI models
- [OpenAI Adapter](./openai.md) - Adapter for direct OpenAI API access

## Using Adapters

Adapters can be used with the `ToolBridge` class:

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig
from llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter

# Create the provider
config = AzureOpenAIConfig(
    api_key="your-api-key",
    endpoint="https://your-endpoint.openai.azure.com",
    deployment_name="your-deployment"
)
provider = AzureOpenAIProvider(config)

# Create an adapter that wraps the provider
adapter = AzureOpenAIAdapter(provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)

# Execute prompts the same way as with direct providers
response = bridge.execute_sync("What is the capital of France?")
print(response.content)  # Output: Paris
```

## Adapter Registry

The `AdapterRegistry` provides dynamic adapter creation and registration:

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry
from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

config = AzureOpenAIConfig(
    api_key="your-api-key",
    endpoint="https://your-endpoint.openai.azure.com",
    deployment_name="your-deployment"
)
provider = AzureOpenAIProvider(config)

# Create an adapter from the registry
adapter = AdapterRegistry.create_adapter("azure_openai", provider)

# Get the class for a specific adapter
adapter_class = AdapterRegistry.get_adapter_class("openai")
```

## Provider Capabilities

Adapters expose provider capabilities through the `get_capabilities()` method:

```python
capabilities = adapter.get_capabilities()

if capabilities.supports_tool_calling:
    print("Provider supports tool calling")
    
if capabilities.supports_multiple_tools:
    print("Provider supports multiple tool calls")

print(f"Maximum token limit: {capabilities.max_tokens_limit}")
```

## Creating Custom Adapters

To create a custom adapter for a provider not yet supported:

1. Create a new class that inherits from `BaseProviderAdapter` 
2. Implement the required methods:
   - `__init__(provider)` - Initialize with a provider
   - `get_capabilities()` - Return capabilities
   - `prepare_request(prompt, tools, tool_results, **kwargs)` - Format requests
   - `execute_request(request)` - Execute the request
   - `parse_response(response)` - Parse the response

3. Register your adapter with the `AdapterRegistry`

Example:

```python
from llm_toolbridge.core.adapter import BaseProviderAdapter, ProviderCapabilities
from llm_toolbridge.core.adapter_registry import AdapterRegistry

class CustomAdapter(BaseProviderAdapter):
    # Implementation...

# Register your adapter
AdapterRegistry.register("custom_provider", CustomAdapter)
```