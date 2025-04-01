# Configuration Management

The Configuration module provides utilities for managing settings and configurations for the LLM Tool Bridge library.

## Overview

The Configuration module provides:

1. A standardized way to define global configuration settings
2. Utilities for loading configuration from files
3. Utilities for saving configuration to files
4. Methods for accessing provider-specific configurations

## Key Classes

### ToolBridgeConfig

The base configuration class for the entire library:

```python
class ToolBridgeConfig(BaseModel):
    """
    Global configuration for the LLM Tool Bridge.
    """
    default_provider: Optional[str] = None
    provider_configs: Dict[str, Dict[str, Any]] = {}
    log_level: str = "INFO"
    cache_dir: Optional[str] = None
```

### ConfigManager

A utility class with static methods for managing configuration:

```python
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
        """Load configuration from a file."""
        # ...
    
    @staticmethod
    def save_config(config: ToolBridgeConfig, config_path: str) -> None:
        """Save configuration to a file."""
        # ...
    
    @staticmethod
    def get_provider_config(provider_name: str, config: Optional[ToolBridgeConfig] = None) -> Dict[str, Any]:
        """Get the configuration for a specific provider."""
        # ...
```

## Basic Usage

### Loading Configuration

```python
from src.core.config import ConfigManager

# Load from default locations
config = ConfigManager.load_config()

# Or specify a config file path
config = ConfigManager.load_config("/path/to/my_config.json")

# Access configuration values
if config.default_provider:
    print(f"Default provider: {config.default_provider}")

# Access provider configurations
for provider_name, provider_config in config.provider_configs.items():
    print(f"Provider: {provider_name}")
```

### Creating and Saving Configuration

```python
from src.core.config import ToolBridgeConfig, ConfigManager

# Create a new configuration
config = ToolBridgeConfig(
    default_provider="azure_openai",
    provider_configs={
        "azure_openai": {
            "api_key": "YOUR_API_KEY",
            "endpoint": "https://YOUR_ENDPOINT.openai.azure.com",
            "deployment_name": "YOUR_DEPLOYMENT",
            "api_version": "2023-12-01-preview"
        }
    },
    log_level="DEBUG",
    cache_dir="/path/to/cache"
)

# Save to a file
ConfigManager.save_config(config, "./my_config.json")
```

### Accessing Provider-Specific Configuration

```python
from src.core.config import ConfigManager

# Get configuration for a specific provider
try:
    azure_config = ConfigManager.get_provider_config("azure_openai")
    print(f"Azure OpenAI endpoint: {azure_config['endpoint']}")
except KeyError:
    print("Azure OpenAI provider not configured")
```

## Configuration Resolution

When loading configuration without specifying a path, the following locations are checked in order:

1. The current directory (`./llm_toolbridge_config.json`)
2. The user's home directory (`~/.llm_toolbridge/config.json`)
3. A path specified by the `LLM_TOOLBRIDGE_CONFIG` environment variable

If no configuration file is found or they are invalid, a default configuration is returned.

## Environment Variable Support

Configuration values can be overridden using environment variables. For example:

- `LLM_TOOLBRIDGE_DEFAULT_PROVIDER` - Override the default provider
- `LLM_TOOLBRIDGE_LOG_LEVEL` - Override the log level
- `LLM_TOOLBRIDGE_CACHE_DIR` - Override the cache directory

Provider-specific environment variables are also supported:

- `LLM_TOOLBRIDGE_AZURE_OPENAI_API_KEY` - Set the Azure OpenAI API key
- `LLM_TOOLBRIDGE_AZURE_OPENAI_ENDPOINT` - Set the Azure OpenAI endpoint

## Best Practices

1. **Use environment variables for sensitive information** like API keys to avoid committing secrets to version control.

2. **Store configuration files outside the application directory** to allow for system-wide configuration.

3. **Set reasonable defaults** to ensure the library works even without explicit configuration.

4. **Validate configuration** when loading to catch errors early.

5. **Use different configuration files for different environments** (development, staging, production).

## Sample Configuration File

```json
{
  "default_provider": "azure_openai",
  "provider_configs": {
    "azure_openai": {
      "api_key": "YOUR_API_KEY",
      "endpoint": "https://YOUR_ENDPOINT.openai.azure.com",
      "deployment_name": "YOUR_DEPLOYMENT",
      "api_version": "2023-12-01-preview"
    },
    "openai": {
      "api_key": "YOUR_OPENAI_API_KEY"
    }
  },
  "log_level": "INFO",
  "cache_dir": "/path/to/cache"
}
```