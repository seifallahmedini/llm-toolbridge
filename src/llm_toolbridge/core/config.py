"""
Configuration module.

This module provides utilities for handling configuration settings
for the LLM Tool Bridge library.
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path

from pydantic import BaseModel


class ToolBridgeConfig(BaseModel):
    """
    Global configuration for the LLM Tool Bridge.
    
    Args:
        default_provider: The default provider to use if none is specified.
        provider_configs: Configuration for each provider.
        log_level: The logging level to use.
        cache_dir: Directory to use for caching.
    """
    default_provider: Optional[str] = None
    provider_configs: Dict[str, Dict[str, Any]] = {}
    log_level: str = "INFO"
    cache_dir: Optional[str] = None


class ConfigManager:
    """Manager for loading and saving LLM Tool Bridge configuration."""
    
    DEFAULT_CONFIG_PATHS = [
        # Current directory
        "./llm_toolbridge_config.json",
        # User's home directory
        str(Path.home() / ".llm_toolbridge" / "config.json"),
        # Environment variable
        os.environ.get("LLM_TOOLBRIDGE_CONFIG", ""),
    ]
    
    @staticmethod
    def load_config(config_path: Optional[str] = None) -> ToolBridgeConfig:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file. If None, searches in default locations.
            
        Returns:
            The loaded configuration.
            
        Raises:
            FileNotFoundError: If no configuration file is found.
        """
        # Use provided path or search default locations
        paths_to_try = [config_path] if config_path else ConfigManager.DEFAULT_CONFIG_PATHS
        
        for path in paths_to_try:
            if not path:
                continue
                
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        config_data = json.load(f)
                    return ToolBridgeConfig(**config_data)
                except (json.JSONDecodeError, IOError) as e:
                    # Log error but continue trying other paths
                    print(f"Error loading config from {path}: {str(e)}")
        
        # If no config file found or all failed to load, return default config
        return ToolBridgeConfig()
    
    @staticmethod
    def save_config(config: ToolBridgeConfig, config_path: str) -> None:
        """
        Save configuration to a file.
        
        Args:
            config: The configuration to save.
            config_path: Path where to save the configuration.
            
        Raises:
            IOError: If the configuration cannot be saved.
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Save the configuration
        with open(config_path, "w") as f:
            f.write(config.model_dump_json(indent=2))
    
    @staticmethod
    def get_provider_config(provider_name: str, config: Optional[ToolBridgeConfig] = None) -> Dict[str, Any]:
        """
        Get the configuration for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            config: The configuration to use. If None, loads from default locations.
            
        Returns:
            The provider configuration.
            
        Raises:
            KeyError: If the provider is not in the configuration.
        """
        if config is None:
            config = ConfigManager.load_config()
            
        if provider_name not in config.provider_configs:
            raise KeyError(f"No configuration found for provider '{provider_name}'")
            
        return config.provider_configs[provider_name]