# Tool Bridge

The `ToolBridge` class is the primary interface for users of the LLM Tool Bridge library. It manages the connection between LLM providers and tools, handling the execution flow and tool calling process.

## Overview

The `ToolBridge` class serves as a central hub that:

1. Manages a collection of registered tools
2. Interfaces with an LLM provider
3. Handles the execution flow of prompts and tool calls
4. Processes tool results and returns final responses

## Class Definition

```python
class ToolBridge:
    def __init__(self, provider: Provider):
        """
        Initialize the ToolBridge with a provider.
        
        Args:
            provider: The LLM provider to use for generating responses.
        """
        # ...
        
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the ToolBridge.
        
        Args:
            tool: The tool to register.
            
        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        # ...
        
    def register_tools(self, tools: List[Tool]) -> None:
        """
        Register multiple tools with the ToolBridge.
        
        Args:
            tools: The tools to register.
            
        Raises:
            ValueError: If any tool with the same name is already registered.
        """
        # ...
            
    def get_tool(self, name: str) -> Tool:
        """
        Get a registered tool by name.
        
        Args:
            name: The name of the tool to retrieve.
            
        Returns:
            The requested tool.
            
        Raises:
            KeyError: If no tool with the given name is registered.
        """
        # ...
        
    async def execute(
        self, 
        prompt: str, 
        tools: Optional[List[Union[Tool, str]]] = None,
        max_tool_calls: int = 10
    ) -> LLMResponse:
        """
        Execute the LLM with the given prompt and tools.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
                   Can be Tool objects or names of registered tools.
            max_tool_calls: Maximum number of tool calls to allow.
                           
        Returns:
            The final LLM response.
        """
        # ...
    
    def execute_sync(
        self, 
        prompt: str, 
        tools: Optional[List[Union[Tool, str]]] = None,
        max_tool_calls: int = 10
    ) -> LLMResponse:
        """
        Synchronous version of execute.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            max_tool_calls: Maximum number of tool calls to allow.
            
        Returns:
            The final LLM response.
        """
        # ...
```

## Usage Examples

### Basic Usage

```python
from src.core import ToolBridge
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig

# Create the provider
config = AzureOpenAIConfig(
    api_key="your-api-key",
    endpoint="https://your-endpoint.openai.azure.com",
    deployment_name="your-deployment"
)
provider = AzureOpenAIProvider(config)

# Create the bridge
bridge = ToolBridge(provider)

# Execute a simple prompt without tools
response = bridge.execute_sync("What is the capital of France?")
print(response.content)  # Paris
```

### Using Tools

```python
from src.core import ToolBridge, Tool

# Define a weather tool
def get_weather(location: str, days: int = 0):
    # Implementation would call a weather API
    return {"location": location, "forecast": "sunny", "days": days}

weather_tool = Tool(
    name="get_weather",
    description="Get the weather forecast for a location",
    parameters={
        "location": {"type": "string", "description": "City or address"},
        "days": {"type": "integer", "description": "Days in the future (0 = today)"}
    },
    function=get_weather
)

# Create and set up the bridge
bridge = ToolBridge(provider)  # Assuming provider is already created
bridge.register_tool(weather_tool)

# Execute a prompt that might use the tool
response = bridge.execute_sync(
    "What's the weather like in Seattle?",
    tools=[weather_tool]
)
print(response)
```

## Tool Execution Flow

The `ToolBridge.execute()` method (and its synchronous counterpart `execute_sync()`) handle the complete flow of:

1. Sending the initial prompt to the LLM provider
2. Receiving the initial response or tool calls
3. If tool calls are present:
   a. Executing each tool with the provided arguments
   b. Sending the tool results back to the LLM
   c. Receiving a new response
4. Repeating until no more tool calls are requested or the maximum call limit is reached
5. Returning the final response

This process enables a natural conversation flow where the LLM can use tools as needed to fulfill the user's request.