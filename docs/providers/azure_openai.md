# Azure OpenAI Provider

This document provides comprehensive setup and usage instructions for the Azure OpenAI provider in the LLM Tool Bridge library.

## Overview

The Azure OpenAI provider allows you to connect to Azure OpenAI's API for chat completions and function calling. Using this provider, you can leverage Azure's hosted OpenAI models (like GPT-4 and GPT-3.5-Turbo) with all the enterprise-grade features of Azure, such as compliance, security, and regional availability.

## Prerequisites

Before using the Azure OpenAI provider, you need:

1. An Azure account with access to Azure OpenAI services
2. An Azure OpenAI deployment with a model that supports function calling (e.g., GPT-4, GPT-3.5-Turbo)
3. Your Azure OpenAI API key
4. Your Azure OpenAI endpoint URL
5. Your deployment name

## Installation

Ensure you have the required dependencies installed:

```bash
pip install llm-toolbridge[azure]
```

Or manually ensure you have the OpenAI Python SDK installed:

```bash
pip install openai>=1.10.0
```

## Configuration

### Configuration Options

The `AzureOpenAIConfig` class provides the following configuration options:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| api_key | str | Azure OpenAI API key | Yes |
| endpoint | str | Azure OpenAI endpoint URL | Yes |
| deployment_name | str | Name of the deployment to use | Yes |
| api_version | str | API version (default: "2023-12-01-preview") | No |
| organization | str | Organization ID (rarely needed for Azure) | No |

### Setup Example

```python
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Create the configuration
config = AzureOpenAIConfig(
    api_key="your-azure-openai-api-key",
    endpoint="https://your-resource-name.openai.azure.com",
    deployment_name="your-deployment-name"
)

# Create the provider
provider = AzureOpenAIProvider(config)
```

### Using Environment Variables

For security, it's better to use environment variables for sensitive information:

```python
import os
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Create the configuration from environment variables
config = AzureOpenAIConfig(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
)

# Create the provider
provider = AzureOpenAIProvider(config)
```

## Basic Usage

### Simple Chat Completion

```python
from src.core.bridge import ToolBridge
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Set up the provider
config = AzureOpenAIConfig(
    api_key="your-azure-openai-api-key",
    endpoint="https://your-resource-name.openai.azure.com",
    deployment_name="your-deployment-name"
)
provider = AzureOpenAIProvider(config)

# Create a bridge
bridge = ToolBridge(provider)

# Generate a response without tools
response = bridge.execute_sync("What is the capital of France?")
print(response.content)  # Output: Paris
```

### Using Tools

To use tools with Azure OpenAI, you need to define and register them:

```python
from src.core.bridge import ToolBridge
from src.core.tool import Tool
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Define a weather tool
def get_weather(location: str, unit: str = "celsius"):
    # In a real implementation, this would call a weather API
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny"
    }

weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a location",
    parameters={
        "location": {"type": "string", "description": "City or address"},
        "unit": {
            "type": "string", 
            "description": "Temperature unit",
            "enum": ["celsius", "fahrenheit"],
            "required": False,
            "default": "celsius"
        }
    },
    function=get_weather
)

# Set up the provider and bridge
config = AzureOpenAIConfig(
    api_key="your-azure-openai-api-key",
    endpoint="https://your-resource-name.openai.azure.com",
    deployment_name="your-deployment-name"
)
provider = AzureOpenAIProvider(config)
bridge = ToolBridge(provider)

# Register the tool with the bridge
bridge.register_tool(weather_tool)

# Execute with the tool available
response = bridge.execute_sync(
    "What's the weather like in Tokyo?",
    tools=[weather_tool]
)

print(response.content)  # Output will include weather information for Tokyo
```

## Advanced Usage

### Custom Parameters

You can customize the generation parameters using keyword arguments:

```python
response = bridge.execute_sync(
    "Write a short poem about nature.",
    tools=None,
    max_tool_calls=5,
    temperature=0.8,
    max_tokens=500,
    top_p=0.95
)
```

### Multiple Tool Calls

Azure OpenAI can make multiple tool calls in a single response. The `ToolBridge` handles this automatically:

```python
# Define multiple tools
calculator_tool = Tool(
    name="calculator",
    description="Perform mathematical calculations",
    parameters={
        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
        "x": {"type": "number"},
        "y": {"type": "number"}
    },
    function=lambda operation, x, y: {
        "add": x + y,
        "subtract": x - y,
        "multiply": x * y,
        "divide": x / y
    }[operation]
)

# Register multiple tools
bridge.register_tools([weather_tool, calculator_tool])

# Execute with multiple tools available
response = bridge.execute_sync(
    "What's the temperature in Paris? And also, what is 25 * 12?",
    max_tool_calls=10  # Allow up to 10 tool calls
)
```

## Error Handling

The Azure OpenAI provider includes comprehensive error handling:

```python
try:
    response = bridge.execute_sync("What is 10 / 0?", tools=[calculator_tool])
except Exception as e:
    print(f"Error: {e}")
    # Handle the error appropriately
```

Common errors include:
- Authentication failures
- Rate limiting
- Invalid requests
- Network issues

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
1. Verify your API key is correct
2. Ensure your subscription has access to Azure OpenAI services
3. Check that the endpoint URL is correct

### Rate Limiting

Azure OpenAI applies rate limits based on your tier. If you hit rate limits:
1. Implement retries with exponential backoff
2. Consider upgrading your service tier
3. Optimize your requests to use fewer tokens

### Function Calling Not Working

If function calling isn't working:
1. Verify your model supports function calling
2. Check tool definitions for errors
3. Make sure the prompt is clear about when to use tools

## Azure OpenAI vs OpenAI

The Azure OpenAI provider differs from the standard OpenAI provider in several ways:

1. **Authentication**: Uses Azure-specific authentication
2. **Endpoint structure**: Uses Azure-specific endpoints with deployments
3. **Compliance**: Offers additional compliance features
4. **Regional deployment**: Allows choosing specific Azure regions

## Further Resources

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [OpenAI Python SDK Documentation](https://github.com/openai/openai-python)
- [Azure OpenAI Function Calling Guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling)