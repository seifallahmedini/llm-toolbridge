# Provider Interface

The `Provider` interface is a key abstraction in the LLM Tool Bridge library that defines how the library interacts with different LLM providers (such as Azure OpenAI, OpenAI, Anthropic, etc.).

## Overview

The `Provider` abstract base class defines the contract that all LLM provider implementations must follow. It encapsulates the logic for:

1. Communicating with specific LLM provider APIs
2. Formatting tools in a provider-specific format
3. Parsing provider-specific responses into a standardized format
4. Handling provider-specific authentication and configuration

## Class Definition

```python
class Provider(ABC):
    @abstractmethod
    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider with the given configuration.
        
        Args:
            config: Provider-specific configuration.
        """
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The LLM's response.
        """
        pass
    
    @abstractmethod
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Format the tools in a way that the provider understands.
        
        Args:
            tools: The tools to format.
            
        Returns:
            The tools formatted for the specific provider.
        """
        pass
    
    @abstractmethod
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        """
        Parse tool calls from the raw provider response.
        
        Args:
            raw_response: The raw response from the provider.
            
        Returns:
            A list of parsed tool calls.
        """
        pass
```

## Related Types

### ProviderConfig

The base configuration class for all providers:

```python
class ProviderConfig(BaseModel):
    """Base configuration for all providers."""
    pass
```

Provider implementations extend this class with their specific configuration requirements.

### ToolCall

Represents a tool call made by an LLM:

```python
class ToolCall(BaseModel):
    """
    Represents a tool call from an LLM.

    Args:
        tool_name: The name of the tool to call.
        arguments: The arguments to pass to the tool.
        call_id: A unique identifier for this tool call.
    """
    tool_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None
```

### LLMResponse

Represents a standardized response from an LLM:

```python
class LLMResponse(BaseModel):
    """
    Represents a response from an LLM.

    Args:
        content: The text response from the LLM.
        tool_calls: Any tool calls requested by the LLM.
    """
    content: Optional[str] = None
    tool_calls: List[ToolCall] = []
```

## Provider Implementation Example

Here's a simplified example of how a provider for Azure OpenAI might be implemented:

```python
class AzureOpenAIConfig(ProviderConfig):
    """Configuration for Azure OpenAI provider."""
    api_key: str
    endpoint: str
    deployment_name: str
    api_version: str = "2023-12-01-preview"
    organization: Optional[str] = None


class AzureOpenAIProvider(Provider):
    """Implementation of the Provider interface for Azure OpenAI."""
    
    def __init__(self, config: AzureOpenAIConfig):
        self.config = config
        self.base_url = f"{config.endpoint}/openai/deployments/{config.deployment_name}"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": config.api_key,
        }
        
        if config.organization:
            self.headers["OpenAI-Organization"] = config.organization
    
    async def generate(
        self, 
        prompt: str, 
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        # Implementation for Azure OpenAI
        # ...
    
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        # Format tools specifically for Azure OpenAI
        # ...
    
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        # Parse tool calls from Azure OpenAI response format
        # ...
```

## Usage Best Practices

1. **Choose the appropriate provider** for your needs based on capabilities and pricing.

2. **Use provider-specific configurations** to fine-tune the behavior of the provider.

3. **Avoid provider-specific code** in your application. Instead, use the abstraction provided by the library.

4. **Handle provider-specific errors** through exception handling around the provider calls.

5. **Be aware of rate limits** and other constraints specific to each provider.

By adhering to the Provider interface, the LLM Tool Bridge library enables a "write once, run anywhere" approach to LLM tool calling, allowing applications to easily switch between different LLM providers without changing application code.