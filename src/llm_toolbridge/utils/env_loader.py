"""
Environment variable loader utility.

This module provides a utility for loading environment variables from a .env file
to simplify configuration of examples and applications.
"""

import os
from pathlib import Path
from typing import Dict, Optional


def load_dotenv(dotenv_path: Optional[str] = None) -> Dict[str, str]:
    """
    Load environment variables from a .env file.

    Args:
        dotenv_path: Path to the .env file. If None, looks for .env in current
                     directory and parent directories.

    Returns:
        Dict of environment variables that were loaded.

    Example:
        >>> load_dotenv()  # Load from .env in current or parent directories
        >>> load_dotenv(".env.development")  # Load from specific file
    """
    # If no path specified, search for .env in current and parent directories
    if dotenv_path is None:
        current_dir = Path.cwd()
        # Try current directory and up to two parent directories
        for dir_path in [current_dir, current_dir.parent, current_dir.parent.parent]:
            potential_path = dir_path / ".env"
            if potential_path.exists():
                dotenv_path = str(potential_path)
                break
    
    # If no .env file found, return empty dict
    if dotenv_path is None or not Path(dotenv_path).exists():
        return {}
    
    # Parse the .env file
    loaded_vars = {}
    with open(dotenv_path, "r") as file:
        for line in file:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
                
            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Set environment variable and track it
                os.environ[key] = value
                loaded_vars[key] = value
    
    return loaded_vars


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable, with optional default value.

    Args:
        key: The name of the environment variable.
        default: Default value if environment variable is not found.

    Returns:
        The value of the environment variable, or the default.
    """
    return os.environ.get(key, default)