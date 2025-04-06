"""
Google Gemini Example.

This example demonstrates how to use Google's Gemini AI model with the LLM Tool Bridge.
It shows both direct provider usage and usage through the adapter interface.
"""

import os
import asyncio
from typing import Dict, List, Any
import random  # Added for weather simulation

from llm_toolbridge.core.bridge import ToolBridge
from src.llm_toolbridge.providers.gemini import GeminiProvider, GeminiConfig
from src.llm_toolbridge.adapters.gemini import GeminiAdapter
from src.llm_toolbridge.core.tool import Tool, ParameterDefinition
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Define a simple calculator tool
calculator_tool = Tool(
    name="calculator",
    description="A simple calculator for arithmetic operations",
    parameters={
        "operation": ParameterDefinition(
            type="string",
            description="The arithmetic operation to perform",
            enum=["add", "subtract", "multiply", "divide"]
        ),
        "x": ParameterDefinition(
            type="number",
            description="The first operand"
        ),
        "y": ParameterDefinition(
            type="number",
            description="The second operand"
        )
    }
)

# Define a weather tool
weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a location",
    parameters={
        "location": ParameterDefinition(
            type="string",
            description="The city and optionally the country (e.g., 'New York, US')"
        ),
        "unit": ParameterDefinition(
            type="string",
            description="Temperature unit (celsius or fahrenheit)",
            enum=["celsius", "fahrenheit"],
            default="celsius"
        )
    }
)


# Define the calculator function
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


# Define the weather function
def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """
    Simulates getting weather for a location.
    
    Args:
        location: The city and optionally the country.
        unit: Temperature unit (celsius or fahrenheit).
        
    Returns:
        Dict containing weather information.
    """
    # In a real application, you would call a weather API here
    # This is a simulation that returns random weather data
    weather_conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "thunderstorm", "snowy"]
    
    # Generate random temperature based on unit
    if unit == "celsius":
        temperature = round(random.uniform(-5, 35), 1)
        temp_unit = "°C"
    else:  # fahrenheit
        temperature = round(random.uniform(20, 95), 1)
        temp_unit = "°F"
    
    # Generate random humidity and wind speed
    humidity = random.randint(30, 95)
    wind_speed = round(random.uniform(0, 30), 1)
    
    # Pick a random weather condition
    condition = random.choice(weather_conditions)
    
    return {
        "location": location,
        "temperature": temperature,
        "unit": temp_unit,
        "condition": condition,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "unit_requested": unit
    }


def direct_provider_example():
    """Example of using the Gemini provider directly."""
    print("\n=== Using Gemini Provider Directly ===")

    # Load environment variables from .env file
    loaded_vars = load_dotenv()
    if loaded_vars:
        print(f"✅ Loaded environment variables from .env file: {', '.join(loaded_vars.keys())}")
    else:
        print("⚠️ No .env file found. Using default values or explicit environment variables.")
    
    # Get API key from environment
    api_key = get_env_var("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set")
        return
        
    # Configure the provider
    config = GeminiConfig(
        api_key=api_key,
        model="gemini-1.5-pro"
    )
    
    # Create provider instance
    provider = GeminiProvider(config)

    # Create the tool bridge with the provider
    bridge = ToolBridge(provider)

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
    
    # Define the weather tool
    weather_tool = Tool(
        name="get_weather",
        description="Get the current weather for a location",
        parameters={
            "location": ParameterDefinition(
                type="string",
                description="The city and optionally the country (e.g., 'New York, US')"
            ),
            "unit": ParameterDefinition(
                type="string",
                description="Temperature unit (celsius or fahrenheit)",
                enum=["celsius", "fahrenheit"],
                default="celsius"
            )
        },
        function=get_weather
    )

    # Register the tools with the bridge
    bridge.register_tool(calculator_tool)
    bridge.register_tool(weather_tool)

    # Updated prompt to demonstrate both tools
    prompt = """
    I need to solve two problems:
    1. If I have 25 apples and give away 7, how many do I have left?
    2. What's the current weather in New York?
    """
    
    # Send a request with tools
    response = bridge.execute_sync(prompt)
    print(f"Response: {response.content}")


if __name__ == "__main__":
    print("Google Gemini Example")
    print("---------------------")
    print("Make sure to set the GOOGLE_API_KEY environment variable.")
    
    # Run the examples
    direct_provider_example()