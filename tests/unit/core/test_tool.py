"""
Unit tests for the tool module.
"""

import pytest
from typing import Dict, Any

from llm_toolbridge.core.tool import Tool, ParameterDefinition


def test_parameter_definition_creation():
    """Test that parameter definitions are created correctly."""
    param = ParameterDefinition(
        type="string",
        description="A test parameter",
        enum=["option1", "option2"],
        required=True,
        default="option1",
    )

    assert param.type == "string"
    assert param.description == "A test parameter"
    assert "option1" in param.enum
    assert param.required is True
    assert param.default == "option1"


def test_parameter_definition_defaults():
    """Test default values for parameter definitions."""
    param = ParameterDefinition(type="integer", description="A test parameter")

    assert param.type == "integer"
    assert param.description == "A test parameter"
    assert param.enum is None
    assert param.required is True
    assert param.default is None


def test_tool_creation():
    """Test that tools are created correctly."""
    # Create a tool with ParameterDefinition objects
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "param1": ParameterDefinition(
                type="string", description="A string parameter"
            ),
            "param2": ParameterDefinition(
                type="integer",
                description="An integer parameter",
                required=False,
                default=0,
            ),
        },
    )

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert "param1" in tool.parameters
    assert isinstance(tool.parameters["param1"], ParameterDefinition)
    assert tool.parameters["param1"].type == "string"
    assert tool.parameters["param2"].default == 0
    assert tool.version == "1.0.0"
    assert tool.function is None


def test_tool_creation_with_dict_parameters():
    """Test creating a tool with dictionary parameter definitions."""
    # Create a tool with dictionary parameters
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "param1": {"type": "string", "description": "A string parameter"},
            "param2": {
                "type": "integer",
                "description": "An integer parameter",
                "required": False,
                "default": 0,
            },
        },
    )

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert "param1" in tool.parameters
    # The implementation converts dictionaries to ParameterDefinition objects
    assert isinstance(tool.parameters["param1"], ParameterDefinition)
    assert tool.parameters["param1"].type == "string"
    assert tool.parameters["param2"].type == "integer"
    assert tool.parameters["param2"].default == 0
    assert not tool.parameters["param2"].required  # Should be False


def test_tool_to_dict():
    """Test converting a tool to a dictionary format suitable for LLM providers."""
    # Create a tool with mixed parameter types
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "param1": ParameterDefinition(
                type="string", description="A string parameter"
            ),
            "param2": {
                "type": "integer",
                "description": "An integer parameter",
                "required": False,
                "default": 0,
            },
        },
    )

    tool_dict = tool.to_dict()

    assert tool_dict["name"] == "test_tool"
    assert tool_dict["description"] == "A test tool"
    assert "properties" in tool_dict["parameters"]
    assert "param1" in tool_dict["parameters"]["properties"]
    assert "param2" in tool_dict["parameters"]["properties"]
    assert "required" in tool_dict["parameters"]
    assert "param1" in tool_dict["parameters"]["required"]
    assert "param2" not in tool_dict["parameters"]["required"]


def test_tool_invoke_success():
    """Test successfully invoking a tool with arguments."""

    # Test function to associate with the tool
    def add_numbers(x: int, y: int) -> int:
        return x + y

    # Create a tool with the function
    tool = Tool(
        name="add",
        description="Add two numbers",
        parameters={
            "x": {"type": "integer", "description": "First number"},
            "y": {"type": "integer", "description": "Second number"},
        },
        function=add_numbers,
    )

    result = tool.invoke({"x": 5, "y": 3})
    assert result == 8


def test_tool_invoke_with_extra_args():
    """Test invoking a tool with extra arguments (edge case)."""

    # Test function that ignores extra arguments
    def greet(name: str, **kwargs) -> str:
        return f"Hello, {name}!"

    # Create a tool with the function
    tool = Tool(
        name="greet",
        description="Greet a person",
        parameters={"name": {"type": "string", "description": "Person's name"}},
        function=greet,
    )

    # Function should work even with extra arguments
    result = tool.invoke({"name": "John", "extra": "ignored"})
    assert result == "Hello, John!"


def test_tool_invoke_failure():
    """Test the failure case when invoking a tool with no function."""
    tool = Tool(
        name="empty_tool",
        description="A tool with no function",
        parameters={"param1": {"type": "string", "description": "A parameter"}},
    )

    # Tool has no function, should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        tool.invoke({"param1": "value"})

    assert "has no associated function" in str(excinfo.value)


def test_tool_missing_required_parameter():
    """Test that required parameters are properly marked in the tool schema."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "required_param": ParameterDefinition(
                type="string", description="A required parameter", required=True
            ),
            "optional_param": ParameterDefinition(
                type="string", description="An optional parameter", required=False
            ),
        },
    )

    tool_dict = tool.to_dict()

    assert "required_param" in tool_dict["parameters"]["required"]
    assert "optional_param" not in tool_dict["parameters"]["required"]


def test_enum_parameters():
    """Test that enum parameters are correctly represented in the tool schema."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={
            "color": ParameterDefinition(
                type="string",
                description="Choose a color",
                enum=["red", "green", "blue"],
            )
        },
    )

    tool_dict = tool.to_dict()

    assert "enum" in tool_dict["parameters"]["properties"]["color"]
    assert tool_dict["parameters"]["properties"]["color"]["enum"] == [
        "red",
        "green",
        "blue",
    ]
