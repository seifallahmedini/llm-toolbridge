# LLM Tool Bridge Examples

This directory contains example implementations demonstrating how to use the LLM Tool Bridge library with different approaches.

## Available Examples

### Provider-Specific Examples

#### Azure OpenAI

1. **Azure OpenAI Direct Provider** (`azure_openai_direct_provider.py`)

   This example demonstrates how to use the LLM Tool Bridge with the direct Provider interface for Azure OpenAI. It shows the traditional approach of creating a provider and using it with the ToolBridge.

   Key concepts demonstrated:
   - Creating and configuring an Azure OpenAI provider
   - Defining and registering tools
   - Manually handling tool calls and responses

2. **Azure OpenAI Adapter** (`azure_openai_adapter.py`)

   This example shows how to use the LLM Tool Bridge with the provider adapter interface for Azure OpenAI, which provides better abstraction and provider-agnostic interactions.

   Key concepts demonstrated:
   - Using the Azure OpenAI adapter for simpler interaction
   - How adapters simplify tool call handling
   - Provider capability introspection

#### OpenAI

3. **OpenAI Adapter** (`openai_adapter.py`)

   This example demonstrates how to use the OpenAI provider with the adapter approach, showing integration with the standard OpenAI API.

   Key concepts demonstrated:
   - Configuring and using the OpenAI provider
   - Working with the OpenAI adapter pattern
   - Processing tool calls with the OpenAI API

#### Google Gemini

4. **Google Gemini Adapter** (`gemini_adapter.py`)

   This example shows how to use Google's Gemini AI models with the LLM Tool Bridge.

   Key concepts demonstrated:
   - Integrating with Google's Generative AI models
   - Using function calling capabilities with Gemini
   - Tool result processing with Gemini

### Advanced Examples

5. **Multi-Provider Switching** (`multi_provider_switching.py`)

   This more advanced example demonstrates how to use the adapter registry to easily switch between different LLM providers without changing application code.

   Key concepts demonstrated:
   - Registering multiple provider adapters
   - Switching between providers at runtime
   - Comparing provider capabilities
   - Using a mock provider for testing and development

## Running the Examples

All examples require the LLM Tool Bridge library to be installed. You can run them from the project root directory:

```bash
# For the Azure OpenAI direct provider example
python -m examples.azure_openai_direct_provider

# For the Azure OpenAI adapter example
python -m examples.azure_openai_adapter

# For the OpenAI adapter example
python -m examples.openai_adapter

# For the Gemini adapter example
python -m examples.gemini_adapter

# For the multi-provider switching example (defaults to mock provider)
python -m examples.multi_provider_switching
# Or with a specific provider
python -m examples.multi_provider_switching azure_openai
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

### OpenAI Credentials

To run examples with OpenAI, set these environment variables:

```bash
# On Windows
set OPENAI_API_KEY=your-api-key
set OPENAI_MODEL=gpt-4

# On Linux/Mac
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=gpt-4
```

### Google Gemini Credentials

To run examples with Google Gemini, set these environment variables:

```bash
# On Windows
set GOOGLE_API_KEY=your-api-key

# On Linux/Mac
export GOOGLE_API_KEY=your-api-key
```

## Using the Mock Provider

The multi-provider switching example includes a mock provider that doesn't require any API keys, making it perfect for testing and development. The mock provider simulates LLM responses and tool calls, so you can develop your application without making actual API calls.