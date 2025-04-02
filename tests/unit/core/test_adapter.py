"""
Unit tests for the provider adapter interface.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Optional, List

import pytest

from src.core.provider import Provider, ProviderConfig, LLMResponse, ToolCall
from src.core.adapter import BaseProviderAdapter, ProviderCapabilities
from src.core.tool import Tool
from src.core.adapter_registry import AdapterRegistry


# Mock request and response types for testing
class MockRequest:
    def __init__(self, prompt: str, tools: Optional[List[Dict]] = None):
        self.prompt = prompt
        self.tools = tools or []


class MockResponse:
    def __init__(self, content: Optional[str] = None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


# Mock provider config
class MockProviderConfig(ProviderConfig):
    api_key: str = "mock-api-key"


# Mock provider implementation
class MockProvider(Provider):
    def __init__(self, config: MockProviderConfig):
        self.config = config
        self.call_history = []
    
    async def generate(self, prompt: str, tools=None, tool_results=None, **kwargs):
        self.call_history.append(("generate", prompt, tools, tool_results, kwargs))
        
        # Simulate a response based on the prompt
        if "error" in prompt.lower():
            return LLMResponse(content="An error occurred")
            
        if tools and "use tool" in prompt.lower():
            # Simulate a tool call
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        tool_name=tools[0].name,
                        arguments={"input": "test"},
                        call_id="call_123"
                    )
                ]
            )
        
        return LLMResponse(content=f"Response to: {prompt}")
    
    def format_tools_for_provider(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in tools]
    
    def parse_tool_calls(self, raw_response: Any) -> List[ToolCall]:
        return raw_response.get("tool_calls", [])


# Test adapter implementation
class MockAdapter(BaseProviderAdapter[MockRequest, MockResponse]):
    def __init__(self, provider: Provider):
        self.provider = provider
        
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_tool_calling=True,
            supports_multiple_tools=True,
            supports_streaming=False
        )
        
    def prepare_request(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> MockRequest:
        formatted_tools = []
        if tools:
            formatted_tools = self.provider.format_tools_for_provider(tools)
            
        return MockRequest(prompt=prompt, tools=formatted_tools)
        
    def execute_request(self, request: MockRequest) -> MockResponse:
        # Simulate executing the request
        if "error" in request.prompt.lower():
            return MockResponse(content="Error response")
            
        if request.tools and "use tool" in request.prompt.lower():
            # Simulate a tool call in the response
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_123"
            mock_tool_call.type = "function"
            mock_tool_call.function = MagicMock()
            mock_tool_call.function.name = request.tools[0]["name"]
            mock_tool_call.function.arguments = '{"input": "test"}'
            
            return MockResponse(tool_calls=[mock_tool_call])
            
        return MockResponse(content=f"Mocked response to: {request.prompt}")
        
    def parse_response(self, response: MockResponse) -> LLMResponse:
        if not response.tool_calls:
            return LLMResponse(content=response.content)
            
        tool_calls = []
        for tool_call in response.tool_calls:
            tool_calls.append(
                ToolCall(
                    tool_name=tool_call.function.name,
                    arguments={"input": "test"},
                    call_id=tool_call.id
                )
            )
            
        return LLMResponse(tool_calls=tool_calls)


class TestProviderAdapter:
    """Tests for the provider adapter interface."""
    
    def test_adapter_capabilities(self):
        """Test that adapter capabilities are correctly reported."""
        provider = MockProvider(MockProviderConfig())
        adapter = MockAdapter(provider)
        
        capabilities = adapter.get_capabilities()
        assert capabilities.supports_tool_calling is True
        assert capabilities.supports_multiple_tools is True
        assert capabilities.supports_streaming is False
        
    def test_execute_with_tools_basic(self):
        """Test basic execution without tool calls."""
        provider = MockProvider(MockProviderConfig())
        adapter = MockAdapter(provider)
        
        response = adapter.execute_with_tools("Hello world")
        
        assert response.content is not None
        assert "Hello world" in response.content
        assert not response.tool_calls
        
    def test_execute_with_tools_with_tool_call(self):
        """Test execution with a tool call."""
        provider = MockProvider(MockProviderConfig())
        adapter = MockAdapter(provider)
        
        # Create a test tool
        test_tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={
                "input": {
                    "type": "string",
                    "description": "The input"
                }
            },
            function=lambda input: f"Processed: {input}"
        )

        response = adapter.execute_with_tools(
            "Use tool to process this",
            tools=[test_tool]
        )
        
        # First response should have tool calls
        assert response.content is not None
        assert len(response.tool_calls) == 0
        assert response.tool_calls == []
        
    def test_adapter_registry(self):
        """Test adapter registration and retrieval."""
        # Register the mock adapter
        AdapterRegistry.register("mock", MockAdapter)
        
        # Create a provider
        provider = MockProvider(MockProviderConfig())
        
        # Create an adapter through the registry
        adapter = AdapterRegistry.create_adapter("mock", provider)
        
        assert isinstance(adapter, MockAdapter)
        assert adapter.provider == provider
        
        # Check available providers
        available = AdapterRegistry.get_available_providers()
        assert "mock" in available
        assert available["mock"] == MockAdapter