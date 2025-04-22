"""
Unit tests for the ToolBridge class in bridge.py.
"""

import pytest
from llm_toolbridge.core.bridge import ToolBridge
from llm_toolbridge.core.tool import Tool, ParameterDefinition
from llm_toolbridge.core.provider import Provider, ProviderConfig, LLMResponse, ToolCall
from llm_toolbridge.core.adapter import BaseProviderAdapter
import asyncio

class DummyProvider(Provider):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._calls = []
    async def generate(self, prompt, tools=None, tool_results=None, **kwargs):
        self._calls.append((prompt, tools, tool_results))
        # Simulate a tool call on first call, then return a final response
        if not tool_results:
            return LLMResponse(content=None, tool_calls=[ToolCall(tool_name="adder", arguments={"a": 1, "b": 2}, call_id="call1")])
        else:
            return LLMResponse(content="Result is 3", tool_calls=[])
    def format_tools_for_provider(self, tools):
        return []
    def parse_tool_calls(self, raw_response):
        return []

class DummyAdapter(BaseProviderAdapter):
    def __init__(self, provider):
        self.provider = provider
        self._calls = []
    def execute_with_tools(self, prompt, tools, max_tool_calls, **kwargs):
        self._calls.append((prompt, tools, max_tool_calls))
        # Simulate a direct response
        return LLMResponse(content="Adapter response", tool_calls=[])
    def execute_request(self, *args, **kwargs):
        return None
    def get_capabilities(self):
        return type('Caps', (), {"supports_tool_calling": True, "supports_multiple_tools": True, "supports_streaming": False, "supports_vision": False, "max_tokens_limit": 4096})()
    def parse_response(self, response):
        return None
    def prepare_request(self, *args, **kwargs):
        return None

def make_tool():
    return Tool(
        name="adder",
        description="Adds two numbers.",
        parameters={
            "a": ParameterDefinition(type="number", description="First number"),
            "b": ParameterDefinition(type="number", description="Second number")
        },
        function=lambda a, b: a + b
    )

def test_register_and_get_tool():
    """Test registering and retrieving a tool."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    tool = make_tool()
    bridge.register_tool(tool)
    assert bridge.get_tool("adder") is tool

def test_register_duplicate_tool_raises():
    """Test registering a tool with duplicate name raises ValueError."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    tool = make_tool()
    bridge.register_tool(tool)
    with pytest.raises(ValueError):
        bridge.register_tool(tool)

def test_get_tool_not_found():
    """Test getting a tool that is not registered raises KeyError."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    with pytest.raises(KeyError):
        bridge.get_tool("notfound")

def test_register_tools_bulk():
    """Test registering multiple tools at once."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    tool1 = make_tool()
    tool2 = Tool(name="multiplier", description="Multiplies two numbers.", parameters={"a": ParameterDefinition(type="number", description="A"), "b": ParameterDefinition(type="number", description="B")}, function=lambda a, b: a * b)
    bridge.register_tools([tool1, tool2])
    assert bridge.get_tool("adder") is tool1
    assert bridge.get_tool("multiplier") is tool2

def test_resolve_tools_expected():
    """Test _resolve_tools with names and objects."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    tool = make_tool()
    bridge.register_tool(tool)
    assert bridge._resolve_tools([tool]) == [tool]
    assert bridge._resolve_tools(["adder"]) == [tool]
    assert bridge._resolve_tools() == [tool]

def test_resolve_tools_invalid_type():
    """Test _resolve_tools with invalid type raises TypeError."""
    bridge = ToolBridge(DummyProvider(ProviderConfig()))
    with pytest.raises(TypeError):
        bridge._resolve_tools([123])

def test_execute_sync_with_adapter():
    """Test execute_sync uses adapter's execute_with_tools."""
    adapter = DummyAdapter(DummyProvider(ProviderConfig()))
    bridge = ToolBridge(adapter)
    tool = make_tool()
    bridge.register_tool(tool)
    resp = bridge.execute_sync("add 1 and 2", [tool])
    assert resp.content == "Adapter response"
    assert adapter._calls[0][0] == "add 1 and 2"

def test_execute_sync_with_provider_expected():
    """Test execute_sync with provider handles tool call loop and returns final response."""
    provider = DummyProvider(ProviderConfig())
    bridge = ToolBridge(provider)
    tool = make_tool()
    bridge.register_tool(tool)
    resp = bridge.execute_sync("add 1 and 2", [tool])
    assert resp.content == "Result is 3"
    # The tool call result is not visible to the user, but the final content is.

def test_execute_sync_with_provider_tool_error():
    """Test execute_sync with provider when tool raises error (failure case)."""
    def bad_tool(a, b):
        raise ValueError("fail!")
    tool = Tool(name="adder", description="bad", parameters={"a": ParameterDefinition(type="number", description="A"), "b": ParameterDefinition(type="number", description="B")}, function=bad_tool)
    provider = DummyProvider(ProviderConfig())
    bridge = ToolBridge(provider)
    bridge.register_tool(tool)
    resp = bridge.execute_sync("add 1 and 2", [tool])
    assert resp.content == "Result is 3" or resp.content is None  # The error is not surfaced in content

