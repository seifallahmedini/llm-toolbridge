# Adapter Registry

The `AdapterRegistry` is a central registry for managing provider adapters in the LLM Tool Bridge library. It facilitates the dynamic discovery and creation of adapters.

## Overview

The `AdapterRegistry` provides a mechanism for:

1. Registering adapter classes by name
2. Creating adapter instances for specific providers
3. Retrieving adapter classes by name
4. Checking for adapter availability

## Class Definition

```python
class AdapterRegistry:
    """
    A registry for provider adapters.
    """
    
    _adapters: Dict[str, Type[BaseProviderAdapter]] = {}
    
    @classmethod
    def register(cls, name: str, adapter_cls: Type[BaseProviderAdapter]) -> None:
        """
        Register an adapter class with a name.
        
        Args:
            name: The name to register the adapter class with.
            adapter_cls: The adapter class to register.
        """
        cls._adapters[name] = adapter_cls
    
    @classmethod
    def get_adapter_class(cls, name: str) -> Type[BaseProviderAdapter]:
        """
        Get an adapter class by name.
        
        Args:
            name: The name of the adapter class to get.
            
        Returns:
            The adapter class registered with the given name.
            
        Raises:
            KeyError: If no adapter is registered with the given name.
        """
        if name not in cls._adapters:
            raise KeyError(f"No adapter registered with name '{name}'")
        return cls._adapters[name]
    
    @classmethod
    def create_adapter(cls, name: str, provider: Provider) -> BaseProviderAdapter:
        """
        Create an adapter instance for a provider.
        
        Args:
            name: The name of the adapter class to use.
            provider: The provider instance to adapt.
            
        Returns:
            An adapter instance for the provider.
            
        Raises:
            KeyError: If no adapter is registered with the given name.
        """
        adapter_cls = cls.get_adapter_class(name)
        return adapter_cls(provider)
    
    @classmethod
    def has_adapter(cls, name: str) -> bool:
        """
        Check if an adapter is registered with a name.
        
        Args:
            name: The name to check for.
            
        Returns:
            True if an adapter is registered with the name, False otherwise.
        """
        return name in cls._adapters
```

## Basic Usage

### Registering an Adapter

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry
from llm_toolbridge.adapters.custom import CustomAdapter

# Register an adapter class
AdapterRegistry.register("custom", CustomAdapter)
```

### Creating an Adapter Instance

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry
from llm_toolbridge.providers.custom import CustomProvider, CustomConfig

# Create a provider
config = CustomConfig(api_key="your-api-key")
provider = CustomProvider(config)

# Create an adapter instance
adapter = AdapterRegistry.create_adapter("custom", provider)
```

### Checking Adapter Availability

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry

# Check if an adapter is available
if AdapterRegistry.has_adapter("azure_openai"):
    print("Azure OpenAI adapter is available")
else:
    print("Azure OpenAI adapter is not available")
```

### Getting an Adapter Class

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry

try:
    # Get an adapter class by name
    adapter_cls = AdapterRegistry.get_adapter_class("openai")
    print(f"Found adapter class: {adapter_cls.__name__}")
except KeyError:
    print("OpenAI adapter not found")
```

## Automatic Registration

Adapters are typically registered automatically when their modules are imported. This happens in the `__init__.py` file of the adapters package:

```python
# From adapters/__init__.py
from llm_toolbridge.core.adapter_registry import AdapterRegistry

# Import and register adapters
try:
    from llm_toolbridge.adapters.openai import OpenAIAdapter
    AdapterRegistry.register("openai", OpenAIAdapter)
except ImportError:
    pass  # Skip if not available

try:
    from llm_toolbridge.adapters.azure_openai import AzureOpenAIAdapter
    AdapterRegistry.register("azure_openai", AzureOpenAIAdapter)
except ImportError:
    pass  # Skip if not available
```

This ensures that all available adapters are registered automatically when the library is imported.

## Creating a Provider-Agnostic Application

The `AdapterRegistry` enables creating applications that can work with any provider:

```python
from llm_toolbridge.core.adapter_registry import AdapterRegistry
from llm_toolbridge.core.bridge import ToolBridge

def create_bridge(provider_type, provider_config):
    """
    Create a ToolBridge instance using any supported provider.
    
    Args:
        provider_type: The type of provider to use ('openai', 'azure_openai', etc.)
        provider_config: Configuration for the provider
        
    Returns:
        A ToolBridge instance
    """
    # Import the provider module dynamically
    provider_module = __import__(f"llm_toolbridge.providers.{provider_type}", 
                                fromlist=[f"{provider_type.title()}Provider"])
    
    # Get the provider class
    provider_cls_name = f"{provider_type.title().replace('_', '')}Provider"
    provider_cls = getattr(provider_module, provider_cls_name)
    
    # Create the provider
    provider = provider_cls(provider_config)
    
    # Create an adapter using the registry
    adapter = AdapterRegistry.create_adapter(provider_type, provider)
    
    # Create and return the bridge
    return ToolBridge(adapter)
```

## Best Practices

1. **Use meaningful names** when registering adapters that match the provider name

2. **Register adapters automatically** when their modules are imported to ensure availability

3. **Check adapter availability** before trying to create adapters for optional dependencies

4. **Handle missing adapters gracefully** by providing fallbacks or clear error messages

5. **Create provider-agnostic code** by using the adapter registry to decouple your application from specific providers