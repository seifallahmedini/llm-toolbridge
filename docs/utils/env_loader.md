# Environment Loader Utility

The environment loader utility provides functions for loading environment variables from `.env` files and retrieving them with fallback values, making configuration management easier and more secure.

## Overview

This utility module offers two main functions:

1. `load_dotenv()` - Load environment variables from a `.env` file
2. `get_env_var()` - Get an environment variable with an optional default value

These functions help you manage configuration securely by keeping sensitive information like API keys out of your code.

## Functions

### load_dotenv

```python
def load_dotenv(dotenv_path: Optional[str] = None) -> Dict[str, str]:
    """
    Load environment variables from a .env file.
    
    Args:
        dotenv_path: Path to the .env file. If None, it looks in the current directory.
        
    Returns:
        A dictionary of environment variables that were loaded.
    """
```

This function loads environment variables from a `.env` file into the actual environment variables. It returns a dictionary of the variables that were loaded.

### get_env_var

```python
def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable with a default value.
    
    Args:
        name: The name of the environment variable.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The value of the environment variable, or the default if not set.
    """
```

This function retrieves an environment variable by name, with an optional default value if the variable isn't set.

## Usage Examples

### Basic Usage

```python
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables from .env file
loaded_vars = load_dotenv()
print(f"Loaded {len(loaded_vars)} environment variables")

# Get an environment variable
api_key = get_env_var("OPENAI_API_KEY")
if api_key:
    print("API key found")
else:
    print("API key not found")

# Get an environment variable with a default value
model = get_env_var("OPENAI_MODEL", "gpt-4")
print(f"Using model: {model}")
```

### Using with Providers

```python
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var
from llm_toolbridge.providers.openai import OpenAIConfig, OpenAIProvider
from llm_toolbridge.core.bridge import ToolBridge

# Load environment variables
load_dotenv()

# Create configuration using environment variables
config = OpenAIConfig(
    api_key=get_env_var("OPENAI_API_KEY"),
    model=get_env_var("OPENAI_MODEL", "gpt-4"),
    organization=get_env_var("OPENAI_ORGANIZATION", None)
)

# Create provider and bridge
provider = OpenAIProvider(config)
bridge = ToolBridge(provider)

# Use the bridge
response = bridge.execute_sync("Hello, world!")
print(response.content)
```

### Custom .env File Location

```python
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load from a specific .env file
loaded_vars = load_dotenv("/path/to/my/custom.env")
print(f"Loaded {len(loaded_vars)} environment variables")
```

## Sample .env File

```
# API Keys
OPENAI_API_KEY=sk-...your-openai-api-key...
AZURE_OPENAI_API_KEY=your-azure-openai-api-key

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2023-12-01-preview

# OpenAI Configuration
OPENAI_MODEL=gpt-4
OPENAI_ORGANIZATION=your-organization-id
```

## Security Considerations

1. **Never commit .env files** to version control. Add `.env` to your `.gitignore` file.

2. **Provide a sample .env file** (like `.env.example`) with the structure but no actual secrets.

3. **Use different .env files** for different environments (development, staging, production).

4. **Set sensible defaults** for non-sensitive configuration values.

## Implementation Details

The `load_dotenv()` function looks for a file named `.env` in the current directory by default. If a file path is provided, it will use that file instead. It reads the file line by line, ignoring comments and blank lines, and sets each environment variable.

The `get_env_var()` function is a thin wrapper around `os.environ.get()` that adds a default value parameter for convenience.

## Best Practices

1. **Store sensitive information** like API keys and secrets in environment variables.

2. **Provide meaningful defaults** for optional configuration values.

3. **Document required environment variables** in your project's README.

4. **Handle missing variables gracefully** by checking if they're set and providing clear error messages.

5. **Use descriptive variable names** with a clear prefix for your application.