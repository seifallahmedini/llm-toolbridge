# OpenAI Provider

This document provides comprehensive setup and usage instructions for the OpenAI provider in the LLM Tool Bridge library.

## Overview

The OpenAI provider allows you to connect directly to OpenAI's API for chat completions and function calling. Using this provider, you can leverage OpenAI's standard API with models like GPT-4 and GPT-3.5-Turbo for tool usage and function calling.

## Prerequisites

Before using the OpenAI provider, you need:

1. An OpenAI account
2. An API key from the OpenAI platform
3. (Optional) An organization ID if you belong to multiple organizations

## Installation

Ensure you have the required dependencies installed:

```bash
pip install llm-toolbridge[openai]
```

Or manually ensure you have the OpenAI Python SDK installed:

```bash
pip install openai>=1.10.0
```

## Configuration

### Configuration Options

The `OpenAIConfig` class provides the following configuration options:

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| api_key | str | OpenAI API key | Yes |
| model | str | Model name (e.g., "gpt-4", "gpt-3.5-turbo") | Yes |
| organization | str | Organization ID for multi-org accounts | No |

### Setup Example

```python
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig

# Create the configuration
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)

# Create the provider
provider = OpenAIProvider(config)
```

### Using Environment Variables

For security, it's better to use environment variables for sensitive information:

```python
import os
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables from .env file
load_dotenv()

# Create the configuration from environment variables
config = OpenAIConfig(
    api_key=get_env_var("OPENAI_API_KEY"),
    model=get_env_var("OPENAI_MODEL", "gpt-4"),
    organization=get_env_var("OPENAI_ORGANIZATION", None)
)

# Create the provider
provider = OpenAIProvider(config)
```

## Basic Usage

### Simple Chat Completion

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig

# Set up the provider
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)
provider = OpenAIProvider(config)

# Create a bridge
bridge = ToolBridge(provider)

# Generate a response without tools
response = bridge.execute_sync("What is the capital of Japan?")
print(response.content)  # Output: Tokyo
```

### Using Tools

To use tools with OpenAI, you need to define and register them:

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.core.tool import Tool
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig

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
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)
provider = OpenAIProvider(config)
bridge = ToolBridge(provider)

# Register the tool with the bridge
bridge.register_tool(weather_tool)

# Execute with the tool available
response = bridge.execute_sync(
    "What's the weather like in New York?",
    tools=[weather_tool]
)

print(response.content)  # Output will include weather information for New York
```

## Advanced Usage

### Custom Parameters

You can customize the generation parameters using keyword arguments:

```python
response = bridge.execute_sync(
    "Write a short poem about space exploration.",
    tools=None,
    max_tool_calls=5,
    temperature=0.8,
    max_tokens=500,
    top_p=0.95
)
```

### Multiple Tool Calls

OpenAI can make multiple tool calls in a single response. The `ToolBridge` handles this automatically:

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

### Using Different Models

OpenAI offers a variety of models with different capabilities and price points:

```python
# For general use
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)

# For cost-effective applications
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo"
)

# For larger context windows
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4-turbo"
)

# For vision capabilities
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4-vision-preview"
)
```

## Error Handling

The OpenAI provider includes comprehensive error handling:

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
- Context length exceeded

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
1. Verify your API key is correct
2. Check that your subscription is active
3. Ensure your organization ID is correct if using one

### Rate Limiting

OpenAI applies rate limits based on your usage tier. If you hit rate limits:
1. Implement retries with exponential backoff
2. Consider upgrading your usage tier
3. Optimize your requests to use fewer tokens

### Function Calling Not Working

If function calling isn't working:
1. Verify your model supports function calling
2. Check tool definitions for errors
3. Make sure the prompt is clear about when to use tools

## OpenAI vs Azure OpenAI

The OpenAI provider differs from the Azure OpenAI provider in several ways:

1. **Authentication**: Uses standard OpenAI API keys (not Azure-specific)
2. **Endpoint**: Uses the standard OpenAI API endpoint
3. **Model selection**: Uses model names directly rather than deployments
4. **Regional restrictions**: Not bound by Azure regional restrictions

## Further Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI Python SDK Documentation](https://github.com/openai/openai-python)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)