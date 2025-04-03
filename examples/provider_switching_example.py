"""
Example of switching between different LLM providers using adapters.

This example demonstrates how to use the adapter registry to easily
switch between different LLM providers without changing application code.
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Try importing directly (works when package is installed)
try:
    from llm_toolbridge.core.bridge import ToolBridge
    from llm_toolbridge.core.tool import Tool, ParameterDefinition
    from llm_toolbridge.core.adapter_registry import AdapterRegistry
    from llm_toolbridge.core.provider import Provider, LLMResponse, ProviderConfig, ToolCall
    from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig
    from llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter
    from llm_toolbridge.core.adapter import BaseProviderAdapter, ProviderCapabilities
    from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var
    
    print("✅ Using installed package imports")
except ImportError:
    # Fall back to development imports if package is not installed
    print("⚠️ Package not installed, using development imports")
    # Add parent directory to the Python path so we can import from 'src'
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.llm_toolbridge.core.bridge import ToolBridge
    from src.llm_toolbridge.core.tool import Tool, ParameterDefinition
    from src.llm_toolbridge.core.adapter_registry import AdapterRegistry
    from src.llm_toolbridge.core.provider import Provider, LLMResponse, ProviderConfig, ToolCall
    from src.llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig
    from src.llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter
    from src.llm_toolbridge.core.adapter import BaseProviderAdapter, ProviderCapabilities
    from src.llm_toolbridge.utils.env_loader import load_dotenv, get_env_var


# Define a simple calculator tool
def calculator(operation: str, x: float, y: float) -> Dict[str, Any]:
    """A simple calculator tool."""
    result = None
    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        if y == 0:
            return {"error": "Division by zero", "result": None}
        result = x / y
    else:
        return {"error": f"Unknown operation: {operation}", "result": None}
    
    return {"operation": operation, "x": x, "y": y, "result": result}


# Mock provider and adapter for demonstration
class MockConfig(ProviderConfig):
    """Configuration for the mock provider."""
    always_use_tools: bool = True


class MockProvider(Provider):
    """A mock provider for demonstration."""
    
    def __init__(self, config: MockConfig):
        """Initialize the mock provider."""
        self.config = config
        
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a mock response."""
        # For demonstration purposes
        if tool_results:
            # If we got tool results, return a text response
            result_str = ", ".join(f"{k}: {v}" for k, v in tool_results.items())
            return LLMResponse(content=f"I used tools and got: {result_str}")
        
        # If we have tools and are configured to use them, return tool calls
        if tools and self.config.always_use_tools:
            # Always choose the first tool for this demo
            tool = tools[0]
            return LLMResponse(
                content=None,
                tool_calls=[
                    LLMResponse.ToolCall(
                        tool_name=tool.name,
                        arguments={"operation": "multiply", "x": 5.2, "y": 3.8},
                        call_id="mock_call_1"
                    )
                ]
            )
        
        # Otherwise return a text response
        return LLMResponse(content=f"Mock response to: {prompt}")
    
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """Format tools for the mock provider."""
        return [tool.to_dict() for tool in tools]
    
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        """Parse tool calls from the raw response."""
        return []


class MockAdapter(BaseProviderAdapter):
    """Adapter for the mock provider."""
    
    def __init__(self, provider: Provider):
        """Initialize the adapter with a provider."""
        self.provider = provider
        
    def get_capabilities(self) -> ProviderCapabilities:
        """Get the capabilities of this provider."""
        return ProviderCapabilities(
            supports_tool_calling=True,
            supports_multiple_tools=True,
            supports_streaming=True,
            supports_vision=False,
            max_tokens_limit=8192  # Different from Azure OpenAI
        )
    
    def prepare_request(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare a provider-specific request."""
        return {
            "prompt": prompt, 
            "tools": tools, 
            "tool_results": tool_results,
            **kwargs
        }
    
    def execute_request(self, request: Dict[str, Any]) -> Any:
        """Execute a prepared request using the provider."""
        prompt = request.pop("prompt")
        tools = request.pop("tools", None)
        tool_results = request.pop("tool_results", None)
        
        if isinstance(self.provider, MockProvider):
            # Simulate sync execution by using a dummy implementation
            if tools and tool_results is None and self.provider.config.always_use_tools:
                # First call - return a tool call
                tool = tools[0]
                return LLMResponse(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            tool_name=tool.name,
                            arguments={"operation": "multiply", "x": 5.2, "y": 3.8},
                            call_id="mock_call_1"
                        )
                    ]
                )
            else:
                # Follow-up call with tool results - return text
                if tool_results:
                    first_result = list(tool_results.values())[0]
                    if isinstance(first_result, dict) and "result" in first_result:
                        answer = first_result["result"]
                        return LLMResponse(
                            content=f"The area of the rectangle is {answer} square units."
                        )
                
                # Default response
                return LLMResponse(content=f"Mock response to: {prompt}")
        else:
            raise TypeError("This adapter only works with MockProvider")
    
    def parse_response(self, response: Any) -> LLMResponse:
        """Parse a provider-specific response into our standard format."""
        return response


def run_example_with_provider(provider_name: str):
    """Run the example with a specific provider."""
    print(f"\n🔄 Running example with {provider_name}...")
    
    # Create the appropriate config and provider
    if provider_name == "azure_openai":
        config = AzureOpenAIConfig(
            api_key=get_env_var("AZURE_OPENAI_API_KEY", "your-api-key"),
            endpoint=get_env_var("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com"),
            deployment_name=get_env_var("AZURE_OPENAI_DEPLOYMENT", "your-deployment-name"),
            api_version=get_env_var("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        )
        provider = AzureOpenAIProvider(config)
        # Use the adapter from the new adapter module
        adapter = AzureOpenAIAdapter(provider)
    else:  # mock provider
        config = MockConfig(always_use_tools=True)
        provider = MockProvider(config)
        adapter = MockAdapter(provider)
    
    # Create the tool bridge with the adapter
    bridge = ToolBridge(adapter)
    
    # Define the calculator tool
    calculator_tool = Tool(
        name="calculator",
        description="Performs mathematical calculations",
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
    
    # Show provider capabilities
    capabilities = adapter.get_capabilities()
    print(f"\n🔍 {provider_name.upper()} Capabilities:")
    print(f"  Tool calling: {capabilities.supports_tool_calling}")
    print(f"  Multiple tools: {capabilities.supports_multiple_tools}")
    print(f"  Streaming: {capabilities.supports_streaming}")
    print(f"  Vision: {capabilities.supports_vision}")
    print(f"  Max tokens: {capabilities.max_tokens_limit}")
    
    # Create a prompt that will use the calculator tool
    prompt = """
    I need to calculate the area of a rectangle with width 5.2 and height 3.8.
    The formula is width multiplied by height. Can you help me?
    """
    
    try:
        # Execute the prompt
        print("\n🔄 Sending prompt to the model...")
        response = bridge.execute_sync(prompt)
        
        # Display the response
        if response.content:
            print(f"\n🤖 Model response: {response.content}")
            
        if response.tool_calls:
            print("\n🔧 Tool calls detected but not automatically processed.")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"  Tool {i+1}: {tool_call.tool_name}")
                print(f"  Arguments: {tool_call.arguments}")
                
    except Exception as e:
        if "azure_openai" in provider_name.lower():
            print(f"\n❌ Error with {provider_name}: {e}")
            print(f"\nNote: The Azure OpenAI example requires valid credentials.")
            print("If you don't have them, try the mock provider example instead:")
            print("  provider_switching_example.py mock")
        else:
            print(f"\n❌ Unexpected error with {provider_name}: {e}")


def main():
    """Run the example."""
    print("LLM Tool Bridge: Provider Switching Example")
    print("-----------------------------------------")
    print("This example demonstrates switching between different LLM providers")
    print("using the adapter pattern.")
    
    # Load environment variables from .env file
    loaded_vars = load_dotenv()
    if loaded_vars:
        print(f"✅ Loaded environment variables from .env file: {', '.join(loaded_vars.keys())}")
    else:
        print("⚠️ No .env file found. Using default values or explicit environment variables.")
    
    # Register our adapters - note that we're now registering manually since
    # we're demonstrating the registration process in this example
    AdapterRegistry.register("azure_openai", AzureOpenAIAdapter)
    AdapterRegistry.register("mock", MockAdapter)
    
    # List available providers
    print("\n📋 Available providers:")
    for provider_name in AdapterRegistry.get_available_providers():
        print(f"  - {provider_name}")
    
    # Choose a provider to run (default to mock for easy demo)
    import sys
    provider_name = sys.argv[1] if len(sys.argv) > 1 else "mock"
    
    # Run the example with the chosen provider
    run_example_with_provider(provider_name)
    
    print("\n✅ Example completed!")
    print("Try running again with a different provider:")
    print("  python provider_switching_example.py azure_openai")
    print("  python provider_switching_example.py mock")


if __name__ == "__main__":
    main()