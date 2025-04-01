# Core Module Documentation

The core module is the foundation of the LLM Tool Bridge library, providing the essential interfaces, classes, and functionality needed to work with LLM providers and their tool calling capabilities.

## Overview

The core module consists of several key components:

- **ToolBridge**: The main interface for interacting with LLM providers and tools
- **Provider**: Abstract base class for LLM provider implementations
- **Tool**: Class for defining and working with tools that can be called by LLMs
- **Configuration**: Utilities for managing configuration settings

## Module Structure

```
core/
├── __init__.py       # Package exports
├── bridge.py         # ToolBridge class implementation
├── config.py         # Configuration utilities
├── provider.py       # Provider interface and response types
├── schema.py         # Request/response schemas
└── tool.py           # Tool definition classes
```

## Usage Example

```python
from src.core import ToolBridge, Tool
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Create a tool
calculator = Tool(
    name="calculator",
    description="Performs basic math operations",
    parameters={
        "operation": {
            "type": "string",
            "enum": ["add", "subtract", "multiply", "divide"],
            "description": "The operation to perform"
        },
        "x": {"type": "number", "description": "First operand"},
        "y": {"type": "number", "description": "Second operand"}
    }
)

# Set up the provider
config = AzureOpenAIConfig(
    api_key="your-api-key",
    endpoint="https://your-endpoint.openai.azure.com",
    deployment_name="your-deployment"
)
provider = AzureOpenAIProvider(config)

# Create the bridge and register the tool
bridge = ToolBridge(provider)
bridge.register_tool(calculator)

# Execute a prompt
response = bridge.execute_sync(
    "Calculate the result of 25 * 12",
    tools=[calculator]
)
print(response)
```

For detailed information about each component, refer to the specific documentation pages:

- [Tool Bridge](./core/bridge.md)
- [Provider Interface](./core/provider.md)
- [Tool Classes](./core/tool.md)
- [Configuration](./core/config.md)
- [Schema Classes](./core/schema.md)