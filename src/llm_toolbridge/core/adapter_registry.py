"""
Provider Adapter Registry module.

This module provides a registry for provider adapters, allowing users
to easily access and manage different provider implementations through
a unified interface.
"""

from typing import Dict, Optional, Type, TypeVar, Generic, Any, Union
import importlib

from .adapter import BaseProviderAdapter
from .provider import Provider, ProviderConfig


T = TypeVar('T', bound=BaseProviderAdapter)


class AdapterRegistry:
    """
    Registry for provider adapters.
    
    This class manages available provider adapters and makes it easy
    to create adapters for specific providers.
    """
    
    _registry: Dict[str, Type[BaseProviderAdapter]] = {}
    
    @classmethod
    def register(cls, provider_name: str, adapter_class: Type[BaseProviderAdapter]) -> None:
        """
        Register an adapter class for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            adapter_class: The adapter class for the provider.
            
        Raises:
            ValueError: If an adapter is already registered for the provider.
        """
        if provider_name in cls._registry:
            raise ValueError(f"Adapter for provider '{provider_name}' is already registered")
            
        cls._registry[provider_name] = adapter_class
        
    @classmethod
    def get_adapter_class(cls, provider_name: str) -> Type[BaseProviderAdapter]:
        """
        Get the adapter class for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            The adapter class for the provider.
            
        Raises:
            KeyError: If no adapter is registered for the provider.
        """
        if provider_name not in cls._registry:
            raise KeyError(f"No adapter registered for provider '{provider_name}'")
            
        return cls._registry[provider_name]
        
    @classmethod
    def create_adapter(cls, provider_name: str, provider: Provider) -> BaseProviderAdapter:
        """
        Create an adapter instance for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            provider: The provider instance.
            
        Returns:
            An instance of the adapter for the provider.
            
        Raises:
            KeyError: If no adapter is registered for the provider.
        """
        adapter_class = cls.get_adapter_class(provider_name)
        return adapter_class(provider)
        
    @classmethod
    def create_from_config(cls, provider_name: str, config: ProviderConfig) -> BaseProviderAdapter:
        """
        Create an adapter from a provider configuration.
        
        This method dynamically imports the provider and creates an adapter for it.
        
        Args:
            provider_name: The name of the provider (e.g., 'azure_openai', 'openai').
            config: The configuration for the provider.
            
        Returns:
            An instance of the adapter for the provider.
            
        Raises:
            ImportError: If the provider module cannot be imported.
            KeyError: If no adapter is registered for the provider.
        """
        try:
            # Import the provider module
            module_path = f"src.providers.{provider_name}"
            module = importlib.import_module(module_path)
            
            # Get the provider class (assuming consistent naming convention)
            provider_class_name = ''.join(word.capitalize() for word in provider_name.split('_')) + 'Provider'
            provider_class = getattr(module, provider_class_name)
            
            # Create provider instance
            provider = provider_class(config)
            
            # Create and return adapter
            return cls.create_adapter(provider_name, provider)
            
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import provider '{provider_name}': {e}")
        
    @classmethod
    def get_available_providers(cls) -> Dict[str, Type[BaseProviderAdapter]]:
        """
        Get all registered providers and their adapter classes.
        
        Returns:
            Dictionary mapping provider names to their adapter classes.
        """
        return cls._registry.copy()