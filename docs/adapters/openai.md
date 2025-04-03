# OpenAI Adapter

This document provides information about the OpenAI adapter in the LLM Tool Bridge library, which enables using OpenAI API services through the adapter interface.

## Overview

The `OpenAIAdapter` provides a standardized interface to the OpenAI provider, allowing applications to interact with OpenAI's API services while maintaining compatibility with the adapter architecture.

## Capabilities

The OpenAI adapter provides the following capabilities:

| Capability | Support | Notes |
|------------|---------|-------|
| Tool Calling | ✅ Yes | Full support for function calling |
| Multiple Tools | ✅ Yes | Can make multiple tool calls in one response |
| Streaming | ❌ No | Not currently supported |
| Vision Models | ✅ Yes | Supports GPT-4 Vision models |
| Max Tokens | 8,192 | Default limit, higher with GPT-4 Turbo |

## Usage

### Basic Setup

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig
from llm_toolbridge.adapters.openai import OpenAIAdapter

# Create the provider
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"  # or "gpt-3.5-turbo" or other models
)
provider = OpenAIProvider(config)

# Create the adapter
adapter = OpenAIAdapter(provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)

# Use the bridge
response = bridge.execute_sync("What is the capital of Italy?")
print(response.content)  # Output: Rome
```

### With Environment Variables

```python
import os
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables from .env file
load_dotenv()

# Create the configuration
config = OpenAIConfig(
    api_key=get_env_var("OPENAI_API_KEY"),
    model=get_env_var("OPENAI_MODEL", "gpt-4"),
    organization=get_env_var("OPENAI_ORGANIZATION", None)
)

# Rest of the setup is the same...
```

### Creating from the Registry

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig
from llm_toolbridge.core.adapter_registry import AdapterRegistry

# Create the provider
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)
provider = OpenAIProvider(config)

# Create the adapter from the registry
adapter = AdapterRegistry.create_adapter("openai", provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)
```

### Using With Tools

```python
from llm_toolbridge.core.tool import Tool, ParameterDefinition

# Define a calculator tool
def calculator(operation: str, x: float, y: float):
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y
    else:
        raise ValueError(f"Unknown operation: {operation}")

calculator_tool = Tool(
    name="calculator",
    description="Perform mathematical calculations",
    parameters={
        "operation": ParameterDefinition(
            type="string",
            description="The operation to perform",
            enum=["add", "subtract", "multiply", "divide"]
        ),
        "x": ParameterDefinition(
            type="number",
            description="First operand"
        ),
        "y": ParameterDefinition(
            type="number",
            description="Second operand"
        )
    },
    function=calculator
)

# Register the tool with the bridge
bridge.register_tool(calculator_tool)

# Execute with the tool available
response = bridge.execute_sync("What is 25 * 12?")
print(response.content)  # Will include the calculation result (300)
```

## Implementation Details

The `OpenAIAdapter` implements the following methods from `BaseProviderAdapter`:

### prepare_request

Formats the request parameters for the OpenAI provider:

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

## Advanced Usage

### Adjusting Model Parameters

You can adjust various parameters when making requests:

```python
response = bridge.execute_sync(
    "Write a short story about a robot that dreams.",
    temperature=0.9,  # Higher creativity
    max_tokens=500,   # Longer response
    top_p=0.95        # More diverse word choices
)
```

### Using Different Models

OpenAI provides multiple models with different capabilities. You can specify the model when creating the config:

```python
# For a standard chat model
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4"
)

# For GPT-4 Turbo with larger context
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-4-turbo"
)

# For a more economical option
config = OpenAIConfig(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo"
)
```

## Error Handling

The adapter standardizes error handling for OpenAI API errors:

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
- Quota exceeded errors
- Invalid request format
- Context length exceeded

## Best Practices

1. **Select the appropriate model** for your needs:
   - GPT-4 for complex reasoning tasks
   - GPT-3.5-Turbo for faster, more economical responses
   - GPT-4-Vision for image analysis

2. **Manage your rate limits** by implementing backoff strategies for retries

3. **Check capabilities before use** to ensure your code works with the provider's features

4. **Use organization IDs** if you're part of multiple organizations to track usage properly

5. **Handle errors gracefully** by catching exceptions and providing fallbacks

6. **Optimize token usage** to reduce costs and improve response times