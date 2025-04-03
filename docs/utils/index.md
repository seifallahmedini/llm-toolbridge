# Utility Modules

This section documents the utility modules provided by the LLM Tool Bridge library, which offer helper functions and utilities to simplify common tasks.

## Available Utilities

- [Environment Loader](./env_loader.md) - Load and retrieve environment variables for secure configuration management

## Overview

The utility modules in LLM Tool Bridge provide helper functions that make it easier to work with the library and manage common tasks. These modules are designed to be simple, focused, and reusable across different parts of your application.

## Using Utilities

Utility modules can be imported directly from the `llm_toolbridge.utils` package:

```python
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables
load_dotenv()

# Get a variable with a default value
api_key = get_env_var("OPENAI_API_KEY", "default-key")
```

## When to Use Utilities

- Use the **environment loader** to securely manage API keys and other sensitive configuration
- Use utilities instead of reimplementing common functionality in your application
- Consider contributing new utility modules for common tasks that could benefit others