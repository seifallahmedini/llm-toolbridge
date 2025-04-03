"""
Example of using the OpenAI provider with the adapter approach.

This example demonstrates how to use the LLM Tool Bridge with the
OpenAI provider through the adapter interface.
"""

import os
import sys
from typing import Dict, Any

# Try importing directly (works when package is installed)
try:
    from llm_toolbridge.core.bridge import ToolBridge
    from llm_toolbridge.core.tool import Tool, ParameterDefinition
    from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig
    from llm_toolbridge.adapters.openai import OpenAIAdapter
    from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var
    
    print("✅ Using installed package imports")
except ImportError:
    # Fall back to development imports if package is not installed
    print("⚠️ Package not installed, using development imports")
    # Add parent directory to the Python path so we can import from 'src'
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.core.bridge import ToolBridge
    from src.core.tool import Tool, ParameterDefinition
    from src.providers.openai import OpenAIProvider, OpenAIConfig
    from src.adapters.openai import OpenAIAdapter
    from src.utils.env_loader import load_dotenv, get_env_var


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
    print("LLM Tool Bridge: OpenAI Provider Example")
    print("---------------------------------------")
    
    # Load environment variables from .env file
    loaded_vars = load_dotenv()
    if loaded_vars:
        print(f"✅ Loaded environment variables from .env file: {', '.join(loaded_vars.keys())}")
    else:
        print("⚠️ No .env file found. Using default values or explicit environment variables.")
    
    # Create the configuration for OpenAI
    config = OpenAIConfig(
        api_key=get_env_var("OPENAI_API_KEY", "your-api-key"),
        model=get_env_var("OPENAI_MODEL", "gpt-4"),
        organization=get_env_var("OPENAI_ORGANIZATION", None),
        base_url=get_env_var("OPENAI_BASE_URL", None)
    )
    
    # Create the provider
    provider = OpenAIProvider(config)
    
    # Create the adapter for the provider using the new adapter path
    adapter = OpenAIAdapter(provider)
    
    # Create the tool bridge with the adapter
    bridge = ToolBridge(adapter=adapter)
    
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
    
    # Create a prompt that will use the calculator tool
    prompt = """
    I need to calculate the area of a rectangle with width 5.2 and height 3.8.
    The formula is width multiplied by height. Can you help me?
    """
    
    try:
        # Execute the prompt with the bridge
        print("\n🔄 Sending prompt to the model...")
        response = bridge.execute_sync(prompt)
        
        # Display the response
        if response.content:
            print(f"\n🤖 Model response: {response.content}")
        
        if response.tool_calls:
            print("\n🔧 Tool calls:")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"  Tool {i+1}: {tool_call.tool_name}")
                print(f"  Arguments: {tool_call.arguments}")
                
                # Execute the tool call
                result = calculator(**tool_call.arguments)
                print(f"  Result: {result}")
                
                # Send the result back to the model
                tool_results = {tool_call.call_id or tool_call.tool_name: result}
                
                print("\n🔄 Sending tool results back to the model...")
                final_response = bridge.execute_sync(prompt, tool_results=tool_results)
                
                print(f"\n🤖 Final response: {final_response.content}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: This example requires valid OpenAI credentials.")
        print("You can set them using a .env file in the project root or as environment variables:")
        print("  OPENAI_API_KEY=your-api-key")
        print("  OPENAI_MODEL=gpt-4")
        

if __name__ == "__main__":
    main()