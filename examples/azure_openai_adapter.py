"""
Example of using the adapter approach with Azure OpenAI.

This example demonstrates how to use the LLM Tool Bridge with the
provider adapter interface, which provides better abstraction and
provider-agnostic interactions.
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Try importing directly (works when package is installed)
try:
    from llm_toolbridge.core.bridge import ToolBridge
    from llm_toolbridge.core.tool import Tool, ParameterDefinition
    from llm_toolbridge.providers.azure_openai import (
        AzureOpenAIProvider,
        AzureOpenAIConfig,
    )
    from llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter
    from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

    print("✅ Using installed package imports")
except ImportError:
    # Fall back to development imports if package is not installed
    print("⚠️ Package not installed, using development imports")
    # Add parent directory to the Python path so we can import from 'src'
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src.llm_toolbridge.core.bridge import ToolBridge
    from src.llm_toolbridge.core.tool import Tool, ParameterDefinition
    from src.llm_toolbridge.providers.azure_openai import (
        AzureOpenAIProvider,
        AzureOpenAIConfig,
    )
    from src.llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter
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


def main():
    """Run the example."""
    print("LLM Tool Bridge: Adapter Example")
    print("--------------------------------")

    # Load environment variables from .env file
    loaded_vars = load_dotenv()
    if loaded_vars:
        print(
            f"✅ Loaded environment variables from .env file: {', '.join(loaded_vars.keys())}"
        )
    else:
        print(
            "⚠️ No .env file found. Using default values or explicit environment variables."
        )

    # Create the configuration for Azure OpenAI
    config = AzureOpenAIConfig(
        api_key=get_env_var("AZURE_OPENAI_API_KEY", "your-api-key"),
        endpoint=get_env_var(
            "AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com"
        ),
        deployment_name=get_env_var("AZURE_OPENAI_DEPLOYMENT", "your-deployment-name"),
        api_version=get_env_var("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
    )

    # Create the provider
    provider = AzureOpenAIProvider(config)

    # Create the adapter using our new import from src.adapters
    adapter = AzureOpenAIAdapter(provider)

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
                enum=["add", "subtract", "multiply", "divide"],
            ),
            "x": ParameterDefinition(type="number", description="First operand"),
            "y": ParameterDefinition(type="number", description="Second operand"),
        },
        function=calculator,
    )

    # Register the tool with the bridge
    bridge.register_tool(calculator_tool)

    # Check provider capabilities through the adapter
    capabilities = adapter.get_capabilities()
    print("\n🔍 Provider capabilities:")
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
        # Execute the prompt using the synchronous method (which now uses the adapter)
        print("\n🔄 Sending prompt to the model...")
        response = bridge.execute_sync(prompt)

        # Display the response
        if response.content:
            print(f"\n🤖 Model response: {response.content}")

        # ToolBridge will automatically handle tool calls via the adapter
        # so we don't need to manually process them like in the direct example
        if not response.tool_calls:
            print("\n✨ Tool calls were processed automatically by the adapter!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: This example requires valid Azure OpenAI credentials to run.")
        print("You can set them using a .env file in the project root:")
        print("  AZURE_OPENAI_API_KEY=your-api-key")
        print("  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com")
        print("  AZURE_OPENAI_DEPLOYMENT=your-deployment-name")


if __name__ == "__main__":
    main()
