# Provider Documentation

This section contains documentation for all supported LLM providers in the LLM Tool Bridge library.

## Available Providers

- [Azure OpenAI](./azure_openai.md) - Connect to Azure-hosted OpenAI models with enterprise features
- [More providers coming soon...]

## Provider Interface

All providers in the LLM Tool Bridge library implement the common Provider interface, which ensures a consistent experience regardless of which underlying LLM service you're using.

For details on the Provider interface, see the [Provider Interface Documentation](../core/provider.md).

## Implementing Custom Providers

If you need to implement a custom provider for an LLM service that isn't officially supported yet, you can create your own by implementing the Provider interface. 

Basic steps:

1. Create a new provider class that inherits from `Provider`
2. Implement the required methods:
   - `__init__(config)` - Initialize with configuration
   - `generate(prompt, tools, tool_results)` - Generate responses
   - `format_tools_for_provider(tools)` - Format tools for your provider
   - `parse_tool_calls(raw_response)` - Parse tool calls from responses

For detailed information on creating custom providers, see the [Custom Provider Guide](./custom_provider.md) (coming soon).