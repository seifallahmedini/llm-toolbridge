"""
Unit tests for the OpenAI provider.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from llm_toolbridge.core.tool import Tool, ParameterDefinition
from llm_toolbridge.core.provider import LLMResponse, ToolCall
from llm_toolbridge.providers.openai import OpenAIProvider, OpenAIConfig


class TestOpenAIProvider:
    """Tests for the OpenAIProvider class."""

    @patch("llm_toolbridge.providers.openai.OpenAI")
    def test_init(self, mock_openai):
        """Test initialization of the provider."""
        config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4",
            organization="test-org",
            base_url="https://api.test-endpoint.com",
        )

        provider = OpenAIProvider(config)

        assert provider.config == config
        assert provider.model == "gpt-4"

        # Verify OpenAI client was initialized correctly
        mock_openai.assert_called_once_with(
            api_key="test-key",
            organization="test-org",
            base_url="https://api.test-endpoint.com",
        )

    def test_format_tools_for_provider(self):
        """Test formatting tools for the OpenAI API."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        with patch("llm_toolbridge.providers.openai.OpenAI"):
            provider = OpenAIProvider(config)

            # Create a test tool with ParameterDefinition
            tool = Tool(
                name="calculator",
                description="Performs mathematical calculations",
                parameters={
                    "operation": ParameterDefinition(
                        type="string",
                        description="The operation to perform",
                        enum=["add", "subtract", "multiply", "divide"],
                    ),
                    "x": ParameterDefinition(
                        type="number", description="First operand"
                    ),
                    "y": ParameterDefinition(
                        type="number", description="Second operand"
                    ),
                },
            )

            # Create a test tool with dict parameters
            tool_with_dict = Tool(
                name="echo",
                description="Echoes the input",
                parameters={
                    "message": {"type": "string", "description": "The message to echo"}
                },
            )

            formatted_tools = provider.format_tools_for_provider([tool, tool_with_dict])

            assert len(formatted_tools) == 2

            # Check first tool
            assert formatted_tools[0]["type"] == "function"
            assert formatted_tools[0]["function"]["name"] == "calculator"
            assert (
                formatted_tools[0]["function"]["description"]
                == "Performs mathematical calculations"
            )
            assert (
                "operation"
                in formatted_tools[0]["function"]["parameters"]["properties"]
            )
            assert formatted_tools[0]["function"]["parameters"]["properties"][
                "operation"
            ]["enum"] == ["add", "subtract", "multiply", "divide"]
            assert "x" in formatted_tools[0]["function"]["parameters"]["properties"]
            assert "y" in formatted_tools[0]["function"]["parameters"]["properties"]
            assert (
                "operation" in formatted_tools[0]["function"]["parameters"]["required"]
            )
            assert "x" in formatted_tools[0]["function"]["parameters"]["required"]
            assert "y" in formatted_tools[0]["function"]["parameters"]["required"]

            # Check second tool with dict parameters
            assert formatted_tools[1]["type"] == "function"
            assert formatted_tools[1]["function"]["name"] == "echo"
            assert (
                "message" in formatted_tools[1]["function"]["parameters"]["properties"]
            )
            assert "message" in formatted_tools[1]["function"]["parameters"]["required"]

    def test_parse_tool_calls(self):
        """Test parsing tool calls from OpenAI API response."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        with patch("llm_toolbridge.providers.openai.OpenAI"):
            provider = OpenAIProvider(config)

            # Create a mock OpenAI API response with tool calls
            mock_response = MagicMock()

            # Mocking the nested structure without relying on specific imports
            mock_function = MagicMock()
            mock_function.name = "calculator"
            mock_function.arguments = '{"operation": "add", "x": 5, "y": 3}'

            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_123"
            mock_tool_call.type = "function"
            mock_tool_call.function = mock_function

            mock_message = MagicMock()
            mock_message.role = "assistant"
            mock_message.content = None
            mock_message.tool_calls = [mock_tool_call]

            mock_choice = MagicMock()
            mock_choice.index = 0
            mock_choice.message = mock_message
            mock_choice.finish_reason = "tool_calls"

            mock_response.choices = [mock_choice]

            tool_calls = provider.parse_tool_calls(mock_response)

            assert len(tool_calls) == 1
            assert tool_calls[0].tool_name == "calculator"
            assert tool_calls[0].call_id == "call_123"
            assert tool_calls[0].arguments == {"operation": "add", "x": 5, "y": 3}

            # Test with invalid JSON in arguments
            mock_invalid_function = MagicMock()
            mock_invalid_function.name = "calculator"
            mock_invalid_function.arguments = "{invalid_json}"

            mock_invalid_tool_call = MagicMock()
            mock_invalid_tool_call.id = "call_456"
            mock_invalid_tool_call.type = "function"
            mock_invalid_tool_call.function = mock_invalid_function

            mock_invalid_message = MagicMock()
            mock_invalid_message.role = "assistant"
            mock_invalid_message.content = None
            mock_invalid_message.tool_calls = [mock_invalid_tool_call]

            mock_invalid_choice = MagicMock()
            mock_invalid_choice.index = 0
            mock_invalid_choice.message = mock_invalid_message
            mock_invalid_choice.finish_reason = "tool_calls"

            mock_invalid_response = MagicMock()
            mock_invalid_response.choices = [mock_invalid_choice]

            tool_calls_invalid = provider.parse_tool_calls(mock_invalid_response)
            assert len(tool_calls_invalid) == 1
            assert tool_calls_invalid[0].arguments == {
                "error": "Invalid JSON in arguments"
            }

    @patch("llm_toolbridge.providers.openai.OpenAI")
    def test_generate_sync_success(self, mock_openai_class):
        """Test successful synchronous generation."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        # Create a mock response using MagicMock
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = "Hello, I'm an AI assistant."
        mock_message.tool_calls = []

        mock_choice = MagicMock()
        mock_choice.index = 0
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        # Set up the mock client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(config)
        response = provider._generate_sync("Hello, how are you?")

        # Verify the response
        assert response.content == "Hello, I'm an AI assistant."
        assert not response.tool_calls

        # Verify the request
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4"
        assert kwargs["messages"][0]["content"] == "Hello, how are you?"

    @patch("llm_toolbridge.providers.openai.OpenAI")
    def test_generate_sync_with_tools(self, mock_openai_class):
        """Test generation with tools."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        # Create a test tool
        tool = Tool(
            name="calculator",
            description="Performs mathematical calculations",
            parameters={
                "operation": ParameterDefinition(
                    type="string",
                    description="The operation to perform",
                    enum=["add", "subtract", "multiply", "divide"],
                ),
                "x": ParameterDefinition(type="number", description="First operand"),
                "y": ParameterDefinition(type="number", description="Second operand"),
            },
        )

        # Create a mock response using MagicMock
        mock_function = MagicMock()
        mock_function.name = "calculator"
        mock_function.arguments = '{"operation": "add", "x": 5, "y": 3}'

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.type = "function"
        mock_tool_call.function = mock_function

        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]

        mock_choice = MagicMock()
        mock_choice.index = 0
        mock_choice.message = mock_message
        mock_choice.finish_reason = "tool_calls"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        # Set up the mock client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(config)
        response = provider._generate_sync("Calculate 5 + 3", [tool])

        # Verify the response
        assert response.content is None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].tool_name == "calculator"
        assert response.tool_calls[0].arguments == {"operation": "add", "x": 5, "y": 3}

        # Verify request contains tools
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert "tools" in kwargs
        assert len(kwargs["tools"]) == 1
        assert kwargs["tools"][0]["function"]["name"] == "calculator"

    @patch("llm_toolbridge.providers.openai.OpenAI")
    def test_generate_sync_with_tool_results(self, mock_openai_class):
        """Test generation with tool results."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        # Create tool results
        tool_results = {"call_123": {"result": 8, "success": True}}

        # Create a mock response
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = "The result is 8"
        mock_message.tool_calls = []

        mock_choice = MagicMock()
        mock_choice.index = 0
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        # Set up the mock client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(config)
        response = provider._generate_sync("What is 5 + 3?", tool_results=tool_results)

        # Verify the response
        assert response.content == "The result is 8"

        # Verify the request contains tool results
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args

        # Check that there are at least 2 messages (user prompt + tool results)
        assert len(kwargs["messages"]) >= 2

        # First message should be user prompt
        assert kwargs["messages"][0]["role"] == "user"
        assert kwargs["messages"][0]["content"] == "What is 5 + 3?"

        # Make sure the assistant and tool messages for tool results are included
        assistant_message_found = False
        tool_message_found = False

        for message in kwargs["messages"][1:]:
            if message.get("role") == "assistant" and "tool_calls" in message:
                assistant_message_found = True
            elif message.get("role") == "tool" and "tool_call_id" in message:
                tool_message_found = True

        assert assistant_message_found
        assert tool_message_found

    @patch("llm_toolbridge.providers.openai.OpenAI")
    def test_generate_sync_error_handling(self, mock_openai_class):
        """Test error handling in generate_sync."""
        config = OpenAIConfig(api_key="test-key", model="gpt-4")

        # Set up the mock client to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(config)

        # Test that the exception is properly caught and re-raised
        with pytest.raises(Exception) as excinfo:
            provider._generate_sync("Hello")

        assert "OpenAI API request failed" in str(excinfo.value)
