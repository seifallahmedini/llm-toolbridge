"""
Unit tests for the Azure OpenAI provider.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest
import requests

from src.core.tool import Tool, ParameterDefinition
from src.core.provider import LLMResponse, ToolCall
from src.providers.azure_openai import AzureOpenAIProvider, AzureOpenAIConfig


class TestAzureOpenAIProvider:
    """Tests for the AzureOpenAIProvider class."""

    def test_init(self):
        """Test initialization of the provider."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        provider = AzureOpenAIProvider(config)
        
        assert provider.config == config
        assert provider.base_url == "https://test-endpoint.openai.azure.com/openai/deployments/test-deployment"
        assert provider.headers == {
            "Content-Type": "application/json",
            "api-key": "test-key",
        }
        
        # Test with organization
        config_with_org = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment",
            organization="test-org"
        )
        provider_with_org = AzureOpenAIProvider(config_with_org)
        assert "OpenAI-Organization" in provider_with_org.headers
        assert provider_with_org.headers["OpenAI-Organization"] == "test-org"
    
    def test_format_tools_for_provider(self):
        """Test formatting tools for the Azure OpenAI API."""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
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
        provider = AzureOpenAIProvider(config)
        
        # Mock response with tool calls
        mock_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "test-deployment",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": "{\"operation\": \"add\", \"x\": 5, \"y\": 3}"
                        }
                    }]
                },
                "finish_reason": "tool_calls"
            }]
        }
        
        tool_calls = provider.parse_tool_calls(mock_response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "calculator"
        assert tool_calls[0].call_id == "call_123"
        assert tool_calls[0].arguments == {"operation": "add", "x": 5, "y": 3}
        
        # Test with invalid JSON in arguments
        mock_response_invalid_json = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "call_456",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": "{invalid_json}"
                        }
                    }]
                }
            }]
        }
        
        tool_calls_invalid = provider.parse_tool_calls(mock_response_invalid_json)
        assert len(tool_calls_invalid) == 1
        assert tool_calls_invalid[0].arguments == {"error": "Invalid JSON in arguments"}
    
    @patch('requests.post')
    def test_generate_sync_success(self, mock_post):
        """Test successful synchronous generation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "test-deployment",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello, I'm an AI assistant."
                },
                "finish_reason": "stop"
            }]
        }
        mock_post.return_value = mock_response
        
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        provider = AzureOpenAIProvider(config)
        
        response = provider._generate_sync("Hello, how are you?")
        
        # Verify the response
        assert response.content == "Hello, I'm an AI assistant."
        assert not response.tool_calls
        
        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["api-key"] == "test-key"
        assert "messages" in kwargs["json"]
        assert kwargs["json"]["messages"][0]["content"] == "Hello, how are you?"
    
    @patch('requests.post')
    def test_generate_sync_with_tools(self, mock_post):
        """Test generation with tools."""
        # Setup mock response with tool calls
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": None,
                    "tool_calls": [{
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": "{\"operation\": \"add\", \"x\": 5, \"y\": 3}"
                        }
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        provider = AzureOpenAIProvider(config)
        
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
        
        response = provider._generate_sync("Calculate 5 + 3", [tool])
        
        # Verify the response
        assert response.content is None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].tool_name == "calculator"
        assert response.tool_calls[0].arguments == {"operation": "add", "x": 5, "y": 3}
        
        # Verify request contains tools
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "tools" in kwargs["json"]
        assert len(kwargs["json"]["tools"]) == 1
        assert kwargs["json"]["tools"][0]["function"]["name"] == "calculator"
    
    @patch('requests.post')
    def test_generate_sync_error_handling(self, mock_post):
        """Test error handling in generate_sync."""
        # Setup mock to raise an exception
        mock_post.side_effect = requests.exceptions.HTTPError("API Error")
        
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test-endpoint.openai.azure.com",
            deployment_name="test-deployment"
        )
        provider = AzureOpenAIProvider(config)
        
        # Test that the exception is properly caught and re-raised
        with pytest.raises(Exception) as excinfo:
            provider._generate_sync("Hello")
        
        assert "API request failed" in str(excinfo.value)