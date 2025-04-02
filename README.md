# LLM Tool Bridge

A unified interface for working with tool calling across different LLM providers.

## Overview

LLM Tool Bridge provides a consistent interface to work with function/tool calling capabilities of various LLM providers, such as Azure OpenAI, OpenAI, Anthropic, and others. This library allows developers to define tools once and use them across different providers without having to rewrite code for each one.

## Features

- Unified interface for tool definitions
- Provider-specific adapters (Azure OpenAI, OpenAI, etc.)
- Consistent request/response schemas
- Support for multiple tool calling
- Type-safe interfaces using Pydantic

## Installation

```bash
# Install from PyPI (once published)
pip install llm-toolbridge

# Install from source
git clone https://github.com/yourusername/llm-toolbridge.git
cd llm-toolbridge
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```python
from llm_toolbridge.core import Tool, ToolBridge
from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider

# Define your tool
calculator_tool = Tool(
    name="calculator",
    description="Performs arithmetic operations",
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

# Create a provider instance
provider = AzureOpenAIProvider(
    api_key="your-azure-openai-api-key",
    endpoint="your-azure-openai-endpoint",
    deployment_name="your-deployment-name"
)

# Create a tool bridge with your provider
bridge = ToolBridge(provider=provider)

# Register your tool
bridge.register_tool(calculator_tool)

# Execute the LLM with the tool
response = bridge.execute(
    prompt="What is 25 multiplied by 12?",
    tools=[calculator_tool]
)

print(response)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-toolbridge.git
cd llm-toolbridge

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

For detailed instructions on running tests, see [TESTING.md](TESTING.md).

Quick testing commands:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.