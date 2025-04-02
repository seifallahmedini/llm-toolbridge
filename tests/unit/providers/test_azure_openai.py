"""
Unit tests for the Azure OpenAI provider.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.core.tool import Tool, ParameterDefinition
from src.core.provider import LLMResponse, ToolCall
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig


class TestAzureOpenAIProvider:
    """Tests for the AzureOpenAIProvider class."""

    @patch('src.providers.azure_openai.AzureOpenAI')
    def test_init(self, mock_azure_openai):
        """Test initialization of the provider."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
        provider = AzureOpenAIProvider(config)
        
        assert provider.config == config
        assert provider.deployment_name == "test-deployment"
        
        # Verify AzureOpenAI client was initialized correctly
        mock_azure_openai.assert_called_once_with(
            api_key="test-key",
            api_version="2023-12-01-preview",
            azure_endpoint="https://test-endpoint.openai.azure.com",
            organization=None
        )
    
    def test_format_tools_for_provider(self):
        """Test formatting tools for the Azure OpenAI API."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
        with patch('src.providers.azure_openai.AzureOpenAI'):
            provider = AzureOpenAIProvider(config)
            
            # Create a test tool with ParameterDefinition
            tool = Tool(
                name="calculator",
                description="Performs mathematical calculations",
                parameters={
                    "operation": ParameterDefinition(
                        type="string",
                        description="The operation to perform",
                        enum=["add", "subtract", "multiply", "divide"]
                    ),
                    "x": ParameterDefinition(
                        type="number",
                        description="First operand"
                    ),
                    "y": ParameterDefinition(
                        type="number",
                        description="Second operand"
                    )
                }
            )
            
            # Create a test tool with dict parameters
            tool_with_dict = Tool(
                name="echo",
                description="Echoes the input",
                parameters={
                    "message": {
                        "type": "string",
                        "description": "The message to echo"
                    }
                }
            )
            
            formatted_tools = provider.format_tools_for_provider([tool, tool_with_dict])
            
            assert len(formatted_tools) == 2
            
            # Check first tool
            assert formatted_tools[0]["type"] == "function"
            assert formatted_tools[0]["function"]["name"] == "calculator"
            assert formatted_tools[0]["function"]["description"] == "Performs mathematical calculations"
            assert "operation" in formatted_tools[0]["function"]["parameters"]["properties"]
            assert formatted_tools[0]["function"]["parameters"]["properties"]["operation"]["enum"] == ["add", "subtract", "multiply", "divide"]
            assert "x" in formatted_tools[0]["function"]["parameters"]["properties"]
            assert "y" in formatted_tools[0]["function"]["parameters"]["properties"]
            assert "operation" in formatted_tools[0]["function"]["parameters"]["required"]
            assert "x" in formatted_tools[0]["function"]["parameters"]["required"]
            assert "y" in formatted_tools[0]["function"]["parameters"]["required"]
            
            # Check second tool with dict parameters
            assert formatted_tools[1]["type"] == "function"
            assert formatted_tools[1]["function"]["name"] == "echo"
            assert "message" in formatted_tools[1]["function"]["parameters"]["properties"]
            assert "message" in formatted_tools[1]["function"]["parameters"]["required"]
    
    def test_parse_tool_calls(self):
        """Test parsing tool calls from Azure OpenAI API response."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
        with patch('src.providers.azure_openai.AzureOpenAI'):
            provider = AzureOpenAIProvider(config)
            
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
            assert tool_calls_invalid[0].arguments == {"error": "Invalid JSON in arguments"}
    
    @patch('src.providers.azure_openai.AzureOpenAI')
    def test_generate_sync_success(self, mock_azure_openai_class):
        """Test successful synchronous generation."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
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
        mock_azure_openai_class.return_value = mock_client
        
        provider = AzureOpenAIProvider(config)
        response = provider._generate_sync("Hello, how are you?")
        
        # Verify the response
        assert response.content == "Hello, I'm an AI assistant."
        assert not response.tool_calls
        
        # Verify the request
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "test-deployment"
        assert kwargs["messages"][0]["content"] == "Hello, how are you?"
    
    @patch('src.providers.azure_openai.AzureOpenAI')
    def test_generate_sync_with_tools(self, mock_azure_openai_class):
        """Test generation with tools."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
        # Create a test tool
        tool = Tool(
            name="calculator",
            description="Performs mathematical calculations",
            parameters={
                "operation": ParameterDefinition(
                    type="string",
                    description="The operation to perform",
                    enum=["add", "subtract", "multiply", "divide"]
                ),
                "x": ParameterDefinition(
                    type="number",
                    description="First operand"
                ),
                "y": ParameterDefinition(
                    type="number",
                    description="Second operand"
                )
            }
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
        mock_azure_openai_class.return_value = mock_client
        
        provider = AzureOpenAIProvider(config)
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
    
    @patch('src.providers.azure_openai.AzureOpenAI')
    def test_generate_sync_error_handling(self, mock_azure_openai_class):
        """Test error handling in generate_sync."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        
        # Set up the mock client to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_azure_openai_class.return_value = mock_client
        
        provider = AzureOpenAIProvider(config)
        
        # Test that the exception is properly caught and re-raised
        with pytest.raises(Exception) as excinfo:
            provider._generate_sync("Hello")
        
        assert "API request failed" in str(excinfo.value)