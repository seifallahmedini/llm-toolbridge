"""
Integration tests for GeminiProvider.

These tests require valid Gemini credentials in environment variables or a .env file:
- GEMINI_API_KEY
- GEMINI_MODEL
"""

import os
import pytest
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.core.tool import Tool, ParameterDefinition
from llm_toolbridge.providers.gemini import GeminiProvider, GeminiConfig
from llm_toolbridge.utils.env_loader import load_dotenv, get_env_var

load_dotenv()


def has_gemini_creds():
    return all(
        [
            os.getenv("GOOGLE_API_KEY"),
            os.getenv("GEMINI_MODEL"),
        ]
    )


@pytest.mark.skipif(not has_gemini_creds(), reason="Gemini credentials not set")
class TestGeminiProviderIntegration:
    def setup_method(self):
        self.config = GeminiConfig(
            api_key=get_env_var("GOOGLE_API_KEY"),
            model=get_env_var("GEMINI_MODEL", "gemini-pro"),
        )
        self.provider = GeminiProvider(self.config)
        self.bridge = ToolBridge(self.provider)
        self.calculator_tool = Tool(
            name="calculator",
            description="Performs basic math",
            parameters={
                "operation": ParameterDefinition(
                    type="string",
                    description="Operation",
                    enum=["add", "subtract", "multiply", "divide"],
                ),
                "x": ParameterDefinition(type="number", description="First operand"),
                "y": ParameterDefinition(type="number", description="Second operand"),
            },
            function=lambda operation, x, y: {
                "result": (
                    x + y
                    if operation == "add"
                    else (
                        x - y
                        if operation == "subtract"
                        else (
                            x * y
                            if operation == "multiply"
                            else (x / y if y != 0 else None)
                        )
                    )
                )
            },
        )
        self.bridge.register_tool(self.calculator_tool)

    def test_expected_use(self):
        """Test a valid prompt that triggers the calculator tool."""
        prompt = "What is 2 plus 3? Use the calculator tool."
        response = self.bridge.execute_sync(prompt)
        assert response.content is not None
        assert isinstance(response.content, str)

    def test_edge_case_empty_prompt(self):
        """Test with an empty prompt (edge case)."""
        prompt = ""
        response = self.bridge.execute_sync(prompt)
        assert response is not None
        assert hasattr(response, "content")

    def test_failure_invalid_api_key(self):
        """Test with an invalid API key (failure case)."""
        bad_config = GeminiConfig(api_key="invalid-key", model=self.config.model)
        bad_provider = GeminiProvider(bad_config)
        bad_bridge = ToolBridge(bad_provider)
        with pytest.raises(Exception):
            bad_bridge.execute_sync("Test with invalid credentials")
