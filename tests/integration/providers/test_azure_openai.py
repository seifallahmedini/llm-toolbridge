"""
Integration tests for AzureOpenAIProvider.

These tests require valid Azure OpenAI credentials in environment variables or a .env file:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_DEPLOYMENT
- AZURE_OPENAI_API_VERSION
"""

import os
import pytest
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.core.tool import Tool, ParameterDefinition
from llm_toolbridge.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

# Load environment variables from .env if present
load_dotenv()

# Helper: skip tests if credentials are missing
def has_azure_openai_creds():
    return all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        os.getenv("AZURE_OPENAI_API_VERSION"),
    ])

@pytest.mark.skipif(not has_azure_openai_creds(), reason="Azure OpenAI credentials not set")
class TestAzureOpenAIProviderIntegration:
    def setup_method(self):
        self.config = AzureOpenAIConfig(
            api_key=get_env_var("AZURE_OPENAI_API_KEY"),
            endpoint=get_env_var("AZURE_OPENAI_ENDPOINT"),
            deployment_name=get_env_var("AZURE_OPENAI_DEPLOYMENT"),
            api_version=get_env_var("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        )
        self.provider = AzureOpenAIProvider(self.config)
        self.bridge = ToolBridge(self.provider)
        self.calculator_tool = Tool(
            name="calculator",
            description="Performs basic math",
            parameters={
                "operation": ParameterDefinition(type="string", description="Operation", enum=["add", "subtract", "multiply", "divide"]),
                "x": ParameterDefinition(type="number", description="First operand"),
                "y": ParameterDefinition(type="number", description="Second operand")
            },
            function=lambda operation, x, y: {"result": x + y if operation == "add" else x - y if operation == "subtract" else x * y if operation == "multiply" else (x / y if y != 0 else None)}
        )
        self.bridge.register_tool(self.calculator_tool)

    def test_expected_use(self):
        """Test a valid prompt that triggers the calculator tool."""
        prompt = "What is 2 plus 3? Use the calculator tool."
        response = self.bridge.execute_sync(prompt)
        assert response.content is not None
        assert isinstance(response.content, str)
        breakpoint()  # Debugging point to inspect the response
        print(f"Response content: {response}")

    def test_edge_case_empty_prompt(self):
        """Test with an empty prompt (edge case)."""
        prompt = ""
        response = self.bridge.execute_sync(prompt)
        # Should return a response, possibly with a warning or empty content
        assert response is not None
        assert hasattr(response, "content")

    def test_failure_invalid_api_key(self):
        """Test with an invalid API key (failure case)."""
        bad_config = AzureOpenAIConfig(
            api_key="invalid-key",
            endpoint=self.config.endpoint,
            deployment_name=self.config.deployment_name,
            api_version=self.config.api_version
        )
        bad_provider = AzureOpenAIProvider(bad_config)
        bad_bridge = ToolBridge(bad_provider)
        with pytest.raises(Exception):
            bad_bridge.execute_sync("Test with invalid credentials")
