# Testing Guide for LLM Tool Bridge

This document provides instructions for running and writing tests for the LLM Tool Bridge project.

## Running Unit Tests

### Prerequisites

Before running the tests, ensure you have:

1. Set up your development environment as described in the main README.md
2. Installed the development dependencies with `pip install -e ".[dev]"`

### Running All Tests

To run the complete test suite:

```bash
# From the project root directory
pytest
```

### Running Specific Tests

You can run tests from specific modules, classes, or individual test functions:

```bash
# Run tests from a specific module
python -m pytest tests/unit/core/test_tool.py -v

# Run tests from a specific class
python -m pytest tests/unit/providers/test_azure_openai.py::TestAzureOpenAIProvider -v

# Run a specific test function
python -m pytest tests/unit/core/test_config.py::test_default_config -v
```

### Running Tests with Coverage

To run tests and generate a coverage report:

```bash
# Run tests with coverage
pytest --cov=src

# Generate a detailed HTML coverage report
pytest --cov=src --cov-report=html
```

After running the HTML coverage report, you can view it by opening `htmlcov/index.html` in your browser.

## Test Structure

The test suite follows a standard structure:

```
tests/
├── unit/           # Unit tests that test individual components in isolation
│   ├── core/       # Tests for core modules
│   └── providers/  # Tests for provider-specific modules
└── integration/    # Tests that verify components work together correctly
```

## Writing New Tests

When adding new features or fixing bugs, always add or update tests to cover your changes.

### Test Guidelines

1. **Use descriptive test names**: Test names should describe what they're testing
2. **Follow the AAA pattern**:
   - **Arrange**: Set up the test conditions
   - **Act**: Call the code being tested
   - **Assert**: Verify the results
3. **Test edge cases**: Don't just test the happy path
4. **Use fixtures**: For common test setup
5. **Mock external dependencies**: Use `unittest.mock` or `pytest.monkeypatch`

### Example Test

```python
def test_tool_invoke_success():
    """Test successfully invoking a tool with arguments."""
    # Arrange: Set up the test data
    def add_numbers(x: int, y: int) -> int:
        return x + y
    
    tool = Tool(
        name="add",
        description="Add two numbers",
        parameters={
            "x": {"type": "integer", "description": "First number"},
            "y": {"type": "integer", "description": "Second number"}
        },
        function=add_numbers
    )
    
    # Act: Call the function being tested
    result = tool.invoke({"x": 5, "y": 3})
    
    # Assert: Verify the result
    assert result == 8
```

## Mocking External Services

For tests that would normally call external APIs (like Azure OpenAI), use mocking:

```python
@patch('src.providers.azure_openai.AzureOpenAI')
def test_azure_openai_provider(mock_azure_openai):
    # Set up mock behavior
    mock_client = MagicMock()
    mock_response = MagicMock()
    # ... set up your mock response
    mock_client.chat.completions.create.return_value = mock_response
    mock_azure_openai.return_value = mock_client
    
    # Use the provider with the mocked client
    provider = AzureOpenAIProvider(config)
    response = provider._generate_sync("Test prompt")
    
    # Assert expectations
    assert response.content == "Expected content"
```

## Continuous Integration

We use GitHub Actions for continuous integration. Every pull request runs the test suite against multiple Python versions.

To see the full CI configuration, check the `.github/workflows` directory.

## Troubleshooting Tests

### Common Issues

1. **Tests failing due to import errors**:
   Make sure you've installed the package in development mode with `pip install -e .`

2. **Tests failing with API credentials**:
   For unit tests, we mock external API calls. Make sure mocks are properly set up.

3. **Tests passing locally but failing in CI**:
   Check for environment-specific issues like path separators (Windows vs. Unix).

### Debugging Tests

For detailed output when tests fail:

```bash
# More verbose output
pytest -v

# Print stdout/stderr even for passing tests
pytest -v --capture=no

# Enter PDB debugger on test failures
pytest --pdb
```