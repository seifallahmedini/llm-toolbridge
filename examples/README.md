# LLM Tool Bridge Examples

This directory contains example implementations demonstrating how to use the LLM Tool Bridge library with different approaches.

## Available Examples

### 1. Direct Provider Example (`direct_provider_example.py`)

This example demonstrates how to use the LLM Tool Bridge with the direct Provider interface for Azure OpenAI. It shows the traditional approach of creating a provider and using it with the ToolBridge.

Key concepts demonstrated:
- Creating and configuring a provider
- Defining and registering tools
- Manually handling tool calls and responses

### 2. Adapter Example (`adapter_example.py`)

This example shows how to use the LLM Tool Bridge with the provider adapter interface, which provides better abstraction and provider-agnostic interactions.

Key concepts demonstrated:
- Creating a provider adapter
- How adapters simplify tool call handling
- Provider capability introspection

### 3. Provider Switching Example (`provider_switching_example.py`)

This more advanced example demonstrates how to use the adapter registry to easily switch between different LLM providers without changing application code.

Key concepts demonstrated:
- Registering multiple provider adapters
- Switching between providers at runtime
- Comparing provider capabilities
- Using a mock provider for testing and development

## Running the Examples

All examples require the LLM Tool Bridge library to be installed. You can run them from the project root directory:

```bash
# For the direct provider example
python -m examples.direct_provider_example

# For the adapter example
python -m examples.adapter_example

# For the provider switching example (defaults to mock provider)
python -m examples.provider_switching_example
# Or with a specific provider
python -m examples.provider_switching_example azure_openai
```

### Azure OpenAI Credentials

To run examples with Azure OpenAI, you need to set the following environment variables:

```bash
# On Windows
set AZURE_OPENAI_API_KEY=your-api-key
set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
set AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# On Linux/Mac
export AZURE_OPENAI_API_KEY=your-api-key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

## Using the Mock Provider

The provider switching example includes a mock provider that doesn't require any API keys, making it perfect for testing and development. The mock provider simulates LLM responses and tool calls, so you can develop your application without making actual API calls.