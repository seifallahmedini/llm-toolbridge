# Adapter Interface

The Adapter module provides a standardized way to interact with different LLM providers through a common interface, allowing applications to be provider-agnostic.

## Overview

The Adapter module defines:

1. The abstract base class for provider adapters
2. The provider capabilities data structure
3. Type definitions for request and response handling

## Key Classes

### BaseProviderAdapter

The primary abstract base class that all provider adapters must implement:

```python
class BaseProviderAdapter(Generic[RequestT, ResponseT], ABC):
    """
    Base class for adapters that allow interacting with providers through a standardized interface.
    
    TypeVars:
        RequestT: The type of the provider-specific request.
        ResponseT: The type of the provider-specific raw response.
    """
    
    @abstractmethod
    def __init__(self, provider: Provider):
        """Initialize the adapter with a provider."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Get the capabilities of this provider."""
        pass
    
    @abstractmethod
    def prepare_request(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> RequestT:
        """Prepare a provider-specific request object."""
        pass
        
    @abstractmethod
    def execute_request(self, request: RequestT) -> ResponseT:
        """Execute a prepared request using the provider."""
        pass
        
    @abstractmethod
    def parse_response(self, response: ResponseT) -> LLMResponse:
        """Parse a provider-specific response into our standard format."""
        pass
```

### ProviderCapabilities

A data structure that defines the capabilities of a provider:

```python
class ProviderCapabilities(BaseModel):
    """
    Capabilities of an LLM provider.
    
    Attributes:
        supports_tool_calling (bool): Whether the provider supports tool calling.
        supports_multiple_tools (bool): Whether the provider supports multiple tools.
        supports_streaming (bool): Whether the provider supports streaming.
        supports_vision (bool): Whether the provider supports vision.
        max_tokens_limit (int): The maximum number of tokens the provider supports.
    """
    
    supports_tool_calling: bool = False
    supports_multiple_tools: bool = False
    supports_streaming: bool = False
    supports_vision: bool = False
    max_tokens_limit: int = 4096
```

## Implementing an Adapter

To implement a new provider adapter, you need to:

1. Create a class that inherits from `BaseProviderAdapter`
2. Implement all the required abstract methods
3. Register it with the `AdapterRegistry`

Here's a simple example adapter for a hypothetical LLM provider:

```python
class SimpleAdapter(BaseProviderAdapter[Dict[str, Any], Dict[str, Any]]):
    def __init__(self, provider: Provider):
        # Verify the provider is of the correct type
        if not isinstance(provider, SimpleProvider):
            raise TypeError("SimpleAdapter requires a SimpleProvider instance")
        self.provider = provider
    
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_tool_calling=True,
            supports_multiple_tools=False,
            supports_streaming=False,
            supports_vision=False,
            max_tokens_limit=2048
        )
    
    def prepare_request(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Format request for the SimpleProvider
        request = {
            "prompt": prompt,
            "tools": tools,
            "tool_results": tool_results
        }
        for key, value in kwargs.items():
            request[key] = value
        return request
    
    def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters and call the provider
        prompt = request.pop("prompt")
        tools = request.pop("tools", None)
        tool_results = request.pop("tool_results", None)
        
        return self.provider.generate_sync(
            prompt=prompt,
            tools=tools,
            tool_results=tool_results,
            **request
        )
    
    def parse_response(self, response: Dict[str, Any]) -> LLMResponse:
        # Parse the SimpleProvider response into the standard LLMResponse
        content = response.get("text", "")
        tool_calls = []
        
        # Parse any tool calls in the response
        raw_tool_calls = response.get("tool_calls", [])
        for raw_call in raw_tool_calls:
            tool_calls.append(ToolCall(
                tool_name=raw_call["name"],
                arguments=raw_call["arguments"],
                call_id=raw_call.get("id")
            ))
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls
        )
```

## Using Adapters with ToolBridge

The `ToolBridge` class can work with either direct providers or adapters:

```python
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.providers.simple import SimpleProvider, SimpleConfig
from llm_toolbridge.adapters.simple import SimpleAdapter

# Create the provider
config = SimpleConfig(api_key="your-api-key")
provider = SimpleProvider(config)

# Create the adapter
adapter = SimpleAdapter(provider)

# Create the bridge with the adapter
bridge = ToolBridge(adapter)

# Use it like any other bridge
response = bridge.execute_sync("Tell me a joke")
```

## Adapter Registry

The `AdapterRegistry` allows dynamic discovery and creation of adapters:

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry

# Register an adapter class with a name
AdapterRegistry.register("simple", SimpleAdapter)

# Create an adapter instance for a provider
adapter = AdapterRegistry.create_adapter("simple", provider)

# Check if an adapter is available
if AdapterRegistry.has_adapter("simple"):
    print("Simple adapter is available")
```

## Benefits of Using Adapters

Using adapters instead of direct providers offers several benefits:

1. **Abstraction**: Hide provider-specific implementation details from your application code

2. **Capability Inspection**: Query provider capabilities at runtime to ensure compatibility

3. **Standardized Error Handling**: Common error handling approach across different providers

4. **Seamless Provider Switching**: Switch providers without changing application code

5. **Extended Features**: Adapters can add functionality beyond what the raw provider offers

## Best Practices

1. **Always check capabilities** before using provider-specific features to ensure compatibility

2. **Handle provider-specific errors** within the adapter, exposing only standardized errors to the application

3. **Minimize provider-specific code** in adapters to maintain a clean abstraction

4. **Register adapters automatically** when they're imported to make discovery seamless

5. **Document adapter capabilities** clearly so users know what features are supported