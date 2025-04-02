"""
Unit tests for the OpenAI adapter.
"""

from unittest.mock import patch, MagicMock
import pytest

from src.core.provider import LLMResponse, ToolCall
from src.core.tool import Tool, ParameterDefinition
from src.providers.openai import OpenAIProvider, OpenAIConfig
from src.providers.openai_adapter import OpenAIAdapter
from src.core.adapter_registry import AdapterRegistry


class TestOpenAIAdapter:
    """Tests for the OpenAIAdapter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4"
        )
        
        with patch('src.providers.openai.OpenAI'):
            self.provider = OpenAIProvider(config)
            self.adapter = OpenAIAdapter(self.provider)
    
    def test_init(self):
        """Test that the adapter correctly validates its provider."""
        # Valid provider should work
        assert self.adapter.provider == self.provider
        
        # Invalid provider type should raise TypeError
        with pytest.raises(TypeError):
            OpenAIAdapter(MagicMock())
    
    def test_get_capabilities(self):
        """Test that adapter capabilities are correctly reported."""
        capabilities = self.adapter.get_capabilities()
        
        assert capabilities.supports_tool_calling is True
        assert capabilities.supports_multiple_tools is True
        assert capabilities.supports_streaming is False
        assert capabilities.supports_vision is True
        assert capabilities.max_tokens_limit == 8192
    
    def test_prepare_request(self):
        """Test preparing a request for the OpenAI provider."""
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
        
        # Prepare a request with tools
        request = self.adapter.prepare_request(
            prompt="Calculate 5 + 3",
            tools=[tool],
            temperature=0.5
        )
        
        assert request["prompt"] == "Calculate 5 + 3"
        assert len(request["tools"]) == 1
        assert request["tools"][0].name == "calculator"
        assert request["temperature"] == 0.5
        assert request["tool_results"] is None
        
        # Prepare a request with tool results
        tool_results = {"call_123": {"result": 8}}
        request_with_results = self.adapter.prepare_request(
            prompt="What is the result?",
            tool_results=tool_results
        )
        
        assert request_with_results["prompt"] == "What is the result?"
        assert request_with_results["tool_results"] == tool_results
    
    def test_execute_request(self):
        """Test executing a request via the adapter."""
        # Mock the provider's _generate_sync method
        self.provider._generate_sync = MagicMock(return_value=LLMResponse(content="Test response"))
        
        # Create a request
        request = {
            "prompt": "Hello",
            "tools": None,
            "tool_results": None,
            "temperature": 0.7
        }
        
        # Execute the request
        response = self.adapter.execute_request(request)
        
        # Verify the provider method was called correctly
        self.provider._generate_sync.assert_called_once_with(
            prompt="Hello",
            tools=None,
            tool_results=None,
            temperature=0.7
        )
        
        # Verify the response
        assert response.content == "Test response"
    
    def test_parse_response(self):
        """Test parsing a response via the adapter."""
        # Create a test response
        test_response = LLMResponse(
            content="Test content",
            tool_calls=[
                ToolCall(
                    tool_name="calculator",
                    arguments={"x": 5, "y": 3},
                    call_id="call_123"
                )
            ]
        )
        
        # Parse the response
        parsed_response = self.adapter.parse_response(test_response)
        
        # The adapter should pass through LLMResponse objects unchanged
        assert parsed_response == test_response
        assert parsed_response.content == "Test content"
        assert len(parsed_response.tool_calls) == 1
        assert parsed_response.tool_calls[0].tool_name == "calculator"
    
    def test_adapter_registry(self):
        """Test that the adapter is correctly registered."""
        # Verify the adapter is registered with the name "openai"
        adapter_class = AdapterRegistry.get_adapter_class("openai")
        assert adapter_class == OpenAIAdapter
        
        # Create an adapter from the registry
        with patch('src.providers.openai.OpenAI'):
            config = OpenAIConfig(api_key="test-key", model="gpt-4")
            provider = OpenAIProvider(config)
            adapter = AdapterRegistry.create_adapter("openai", provider)
            
            assert isinstance(adapter, OpenAIAdapter)
            assert adapter.provider == provider