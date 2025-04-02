"""
Configuration file for pytest that ensures the 'src' module can be imported in tests.

This file is automatically discovered by pytest when running tests and helps
set up the correct import paths.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python's path
# This allows imports from 'src' to work correctly in test files
project_root = Path(__file__).parent.parent  # tests/ -> project root
sys.path.insert(0, str(project_root))