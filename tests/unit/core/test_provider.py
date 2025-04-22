"""
Unit tests for the provider module.
"""

import pytest
from typing import Dict, Any, List
from pydantic import ValidationError

from llm_toolbridge.core.provider import ProviderConfig, ToolCall, LLMResponse, Provider

# Dummy Tool for type hints
def dummy_tool():
    pass

class DummyProvider(Provider):
    """
    Dummy implementation of Provider for testing abstract methods.
    """
    def __init__(self, config: ProviderConfig):
        self.config = config

    async def generate(self, prompt: str, tools=None, tool_results=None, **kwargs):
        return LLMResponse(content="test", tool_calls=[])

    def format_tools_for_provider(self, tools):
        return []

    def parse_tool_calls(self, raw_response):
        return []

def test_provider_config_instantiation():
    """Test ProviderConfig can be instantiated (even if empty)."""
    config = ProviderConfig()
    assert isinstance(config, ProviderConfig)

def test_tool_call_instantiation():
    """Test ToolCall model instantiation and field values."""
    tc = ToolCall(tool_name="my_tool", arguments={"a": 1, "b": 2}, call_id="abc123")
    assert tc.tool_name == "my_tool"
    assert tc.arguments == {"a": 1, "b": 2}
    assert tc.call_id == "abc123"

def test_tool_call_missing_required():
    """Test ToolCall fails if required fields are missing (failure case)."""
    with pytest.raises(ValidationError):
        ToolCall(arguments={"a": 1})  # tool_name missing

def test_llm_response_instantiation():
    """Test LLMResponse model instantiation and default values."""
    resp = LLMResponse(content="hello", tool_calls=[])
    assert resp.content == "hello"
    assert resp.tool_calls == []

    # Edge: no content, only tool_calls
    resp2 = LLMResponse(tool_calls=[ToolCall(tool_name="t", arguments={})])
    assert resp2.content is None
    assert isinstance(resp2.tool_calls, list)

def test_provider_abstract_instantiation():
    """Test that Provider cannot be instantiated directly (failure case)."""
    with pytest.raises(TypeError):
        Provider(ProviderConfig())

def test_dummy_provider_implements_interface():
    """Test that a concrete Provider subclass can be instantiated and used."""
    config = ProviderConfig()
    provider = DummyProvider(config)
    assert isinstance(provider, Provider)

import asyncio

def test_dummy_provider_generate():
    """Test DummyProvider's generate method returns an LLMResponse."""
    provider = DummyProvider(ProviderConfig())
    result = asyncio.run(provider.generate("prompt"))
    assert isinstance(result, LLMResponse)
    assert result.content == "test"

def test_dummy_provider_format_tools_for_provider():
    """Test DummyProvider's format_tools_for_provider returns a list."""
    provider = DummyProvider(ProviderConfig())
    assert provider.format_tools_for_provider([]) == []

def test_dummy_provider_parse_tool_calls():
    """Test DummyProvider's parse_tool_calls returns a list."""
    provider = DummyProvider(ProviderConfig())
    assert provider.parse_tool_calls(None) == []
