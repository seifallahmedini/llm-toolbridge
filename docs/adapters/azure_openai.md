# Azure OpenAI Adapter

This document provides information about the Azure OpenAI adapter in the LLM Tool Bridge library, which enables using Azure OpenAI services through the adapter interface.

## Overview

The `AzureOpenAIAdapter` provides a standardized interface to the Azure OpenAI provider, allowing applications to interact with Azure OpenAI services while maintaining compatibility with the adapter architecture.

## Capabilities

The Azure OpenAI adapter provides the following capabilities:

| Capability | Support | Notes |
|------------|---------|-------|
| Tool Calling | ✅ Yes | Full support for function calling |
| Multiple Tools | ✅ Yes | Can make multiple tool calls in one response |
| Streaming | ❌ No | Not currently supported |
| Vision Models | ✅ Yes | Supports GPT-4V through Azure |
| Max Tokens | 4,096 | Default limit, varies by model |

## Usage

### Basic Setup

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

# Create the adapter
adapter = AzureOpenAIAdapter(provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)

# Use the bridge
response = bridge.execute_sync("What is the capital of France?")
print(response.content)  # Output: Paris
```

### With Environment Variables

```python
import os
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables from .env file
load_dotenv()

# Create the configuration
config = AzureOpenAIConfig(
    api_key=get_env_var("AZURE_OPENAI_API_KEY"),
    endpoint=get_env_var("AZURE_OPENAI_ENDPOINT"),
    deployment_name=get_env_var("AZURE_OPENAI_DEPLOYMENT"),
    api_version=get_env_var("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
)

# Rest of the setup is the same...
```

### Creating from the Registry

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig
from llm_toolbridge.core.adapter_registry import AdapterRegistry

# Create the provider
config = AzureOpenAIConfig(
    api_key="your-api-key",
    endpoint="https://your-endpoint.openai.azure.com",
    deployment_name="your-deployment"
)
provider = AzureOpenAIProvider(config)

# Create the adapter from the registry
adapter = AdapterRegistry.create_adapter("azure_openai", provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)
```

## Implementing Details

The `AzureOpenAIAdapter` implements the following methods from `BaseProviderAdapter`:

### prepare_request

Formats the request parameters for the Azure OpenAI provider:

```python
def prepare_request(
    self,
    prompt: str,
    tools: Optional[List[Tool]] = None,
    tool_results: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    # Creates a dictionary with the request parameters
    request = {
        "prompt": prompt,
        "tools": tools,
        "tool_results": tool_results
    }
    
    # Add any additional parameters
    for key, value in kwargs.items():
        request[key] = value
        
    return request
```

### execute_request

Sends the request to the provider:

```python
def execute_request(self, request: Dict[str, Any]) -> Any:
    # Extract parameters
    prompt = request.pop("prompt")
    tools = request.pop("tools", None)
    tool_results = request.pop("tool_results", None)
    
    # Call the provider's synchronous generate method
    return self.provider._generate_sync(
        prompt=prompt,
        tools=tools,
        tool_results=tool_results,
        **request
    )
```

### parse_response

Parses the provider's response:

```python
def parse_response(self, response: Any) -> LLMResponse:
    # The response is already in the correct format
    return response
```

## Error Handling

The adapter provides standardized error handling for Azure OpenAI API errors:

```python
try:
    response = bridge.execute_sync("What is 10 / 0?", tools=[calculator_tool])
except Exception as e:
    print(f"Error: {e}")
    # Handle the error appropriately
```

Common error types:
- Authentication errors
- Rate limit errors
- Service availability issues
- Invalid request errors

## Best Practices

1. **Use environment variables** for API keys and other sensitive information

2. **Check capabilities before use** to ensure your code works with the provider's features:
   ```python
   capabilities = adapter.get_capabilities()
   if capabilities.supports_multiple_tools:
       # Use multiple tool calls
   ```

3. **Handle errors gracefully** by catching exceptions and providing fallbacks when services are unavailable

4. **Optimize token usage** by keeping prompts concise, especially when working with models with smaller context limits