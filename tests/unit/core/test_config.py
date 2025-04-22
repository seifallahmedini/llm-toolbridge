"""
Unit tests for the configuration module.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest

from llm_toolbridge.core.config import ToolBridgeConfig, ConfigManager


def test_default_config():
    """Test that default configuration is created correctly."""
    config = ToolBridgeConfig()
    assert config.default_provider is None
    assert config.provider_configs == {}
    assert config.log_level == "INFO"
    assert config.cache_dir is None


def test_config_with_values():
    """Test that configuration with values is created correctly."""
    config = ToolBridgeConfig(
        default_provider="azure_openai",
        provider_configs={
            "azure_openai": {
                "api_key": "test_key",
                "endpoint": "https://test-endpoint.openai.azure.com",
                "deployment_name": "gpt-4",
            }
        },
        log_level="DEBUG",
        cache_dir="/tmp/cache",
    )

    assert config.default_provider == "azure_openai"
    assert "azure_openai" in config.provider_configs
    assert config.provider_configs["azure_openai"]["api_key"] == "test_key"
    assert config.log_level == "DEBUG"
    assert config.cache_dir == "/tmp/cache"


def test_save_and_load_config():
    """Test saving and loading configuration."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp_path = temp.name

    try:
        # Create and save a config
        config = ToolBridgeConfig(
            default_provider="azure_openai",
            provider_configs={
                "azure_openai": {
                    "api_key": "test_key",
                    "endpoint": "https://test-endpoint.openai.azure.com",
                }
            },
        )
        ConfigManager.save_config(config, temp_path)

        # Load the config and verify
        loaded_config = ConfigManager.load_config(temp_path)
        assert loaded_config.default_provider == "azure_openai"
        assert "azure_openai" in loaded_config.provider_configs
        assert loaded_config.provider_configs["azure_openai"]["api_key"] == "test_key"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_load_nonexistent_config():
    """Test loading a configuration that doesn't exist returns default config."""
    # Use a path that definitely doesn't exist
    non_existent_path = "/path/to/nonexistent/config.json"
    config = ConfigManager.load_config(non_existent_path)

    # Should return default config
    assert isinstance(config, ToolBridgeConfig)
    assert config.default_provider is None
    assert config.provider_configs == {}


def test_load_invalid_json_config():
    """Test loading an invalid JSON file returns default config."""
    # Create a temporary file with invalid JSON
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(b"This is not valid JSON")
        temp_path = temp.name

    try:
        # Should return default config without raising an exception
        config = ConfigManager.load_config(temp_path)
        assert isinstance(config, ToolBridgeConfig)
        assert config.default_provider is None
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_get_provider_config():
    """Test getting provider-specific configuration."""
    config = ToolBridgeConfig(
        provider_configs={
            "azure_openai": {
                "api_key": "test_key",
                "endpoint": "https://test-endpoint.openai.azure.com",
            },
            "openai": {"api_key": "another_key"},
        }
    )

    azure_config = ConfigManager.get_provider_config("azure_openai", config)
    assert azure_config["api_key"] == "test_key"

    openai_config = ConfigManager.get_provider_config("openai", config)
    assert openai_config["api_key"] == "another_key"


def test_get_nonexistent_provider_config():
    """Test getting configuration for a provider that doesn't exist raises KeyError."""
    config = ToolBridgeConfig(
        provider_configs={"azure_openai": {"api_key": "test_key"}}
    )

    with pytest.raises(KeyError):
        ConfigManager.get_provider_config("nonexistent", config)


def test_create_dirs_on_save():
    """Test that directories are created when saving to a nested path."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        nested_path = os.path.join(temp_dir, "nested", "path", "config.json")

        config = ToolBridgeConfig(default_provider="azure_openai")

        # Should create directories and not raise an exception
        ConfigManager.save_config(config, nested_path)

        # Verify file was created
        assert os.path.exists(nested_path)
