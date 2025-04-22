"""
Unit tests for the schema module.
"""

import pytest
from pydantic import ValidationError
from llm_toolbridge.core.schema import ToolBridgeRequest, ToolResult, ToolBridgeResponse
from llm_toolbridge.core.tool import Tool, ParameterDefinition

def make_valid_tool() -> Tool:
    """
    Create a valid Tool instance for testing.

    Returns:
        Tool: A valid Tool instance.
    """
    return Tool(
        name="adder",
        description="Adds two numbers.",
        parameters={
            "a": ParameterDefinition(type="number", description="First number", required=True),
            "b": ParameterDefinition(type="number", description="Second number", required=True)
        },
        version="1.0.0"
    )

def test_tool_bridge_request_expected_use():
    """
    Test ToolBridgeRequest with all fields provided.
    """
    tool = make_valid_tool()
    req = ToolBridgeRequest(
        prompt="Test prompt",
        tools=[tool],
        model="gpt-4",
        temperature=0.7,
        max_tokens=100
    )
    assert req.prompt == "Test prompt"
    assert req.tools is not None
    assert req.model == "gpt-4"
    assert req.temperature == 0.7
    assert req.max_tokens == 100

def test_tool_bridge_request_edge_case():
    """
    Test ToolBridgeRequest with only required field.
    """
    req = ToolBridgeRequest(prompt="Only prompt")
    assert req.prompt == "Only prompt"
    assert req.tools is None
    assert req.model is None
    assert req.temperature is None
    assert req.max_tokens is None

def test_tool_bridge_request_failure_case():
    """
    Test ToolBridgeRequest fails if prompt is missing.
    """
    with pytest.raises(ValidationError):
        ToolBridgeRequest()

def test_tool_result_expected_use():
    """
    Test ToolResult with all fields provided.
    """
    result = ToolResult(
        tool_name="my_tool",
        call_id="abc123",
        result={"output": 42},
        error=None,
        success=True
    )
    assert result.tool_name == "my_tool"
    assert result.call_id == "abc123"
    assert result.result == {"output": 42}
    assert result.error is None
    assert result.success is True

def test_tool_result_edge_case():
    """
    Test ToolResult with only required fields.
    """
    result = ToolResult(tool_name="t")
    assert result.tool_name == "t"
    assert result.call_id is None
    assert result.result is None
    assert result.error is None
    assert result.success is True

def test_tool_result_failure_case():
    """
    Test ToolResult fails if tool_name is missing.
    """
    with pytest.raises(ValidationError):
        ToolResult()

def test_tool_bridge_response_expected_use():
    """
    Test ToolBridgeResponse with all fields provided.
    """
    resp = ToolBridgeResponse(
        content="LLM output",
        tool_results=[ToolResult(tool_name="t")],
        provider_name="openai",
        usage={"tokens": 10}
    )
    assert resp.content == "LLM output"
    assert isinstance(resp.tool_results, list)
    assert resp.provider_name == "openai"
    assert resp.usage == {"tokens": 10}

def test_tool_bridge_response_edge_case():
    """
    Test ToolBridgeResponse with only required fields.
    """
    resp = ToolBridgeResponse(provider_name="azure")
    assert resp.content is None
    assert resp.tool_results == []
    assert resp.provider_name == "azure"
    assert resp.usage is None

def test_tool_bridge_response_failure_case():
    """
    Test ToolBridgeResponse fails if provider_name is missing.
    """
    with pytest.raises(ValidationError):
        ToolBridgeResponse()
