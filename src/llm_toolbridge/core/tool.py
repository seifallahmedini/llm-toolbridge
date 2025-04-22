"""
Tool definition module.

This module provides the core Tool class and related types for defining
tools that can be used by LLMs.
"""

from typing import Any, Dict, List, Literal, Optional, Union, Callable
from pydantic import BaseModel, Field


class ParameterDefinition(BaseModel):
    """
    Definition of a parameter for a tool.

    Args:
        type: The JSON Schema type of the parameter.
        description: A description of the parameter.
        enum: Optional list of allowed values for the parameter.
        required: Whether the parameter is required.
        default: Default value for the parameter if not provided.
    """

    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    enum: Optional[List[Any]] = None
    required: bool = True
    default: Optional[Any] = None


class Tool(BaseModel):
    """
    Definition of a tool that can be used by an LLM.

    Args:
        name: The name of the tool.
        description: A description of the tool.
        parameters: The parameters for the tool.
        version: The version of the tool.
        function: The function to be called when this tool is invoked.
    """

    name: str
    description: str
    parameters: Dict[str, Union[ParameterDefinition, Dict[str, Any]]]
    version: str = "1.0.0"
    function: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary suitable for sending to LLM providers.

        Returns:
            Dict representation of the tool.
        """
        result = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            # "version": self.version,
        }

        for param_name, param_def in self.parameters.items():
            if isinstance(param_def, dict):
                # Make a copy to avoid modifying the original dict
                param_dict = param_def.copy()
                # Remove null values from parameter definition
                param_dict = {k: v for k, v in param_dict.items() if v is not None}
                # Ensure enum is never null but a list or removed entirely
                if "enum" in param_dict and param_dict["enum"] is None:
                    del param_dict["enum"]
                result["parameters"]["properties"][param_name] = param_dict
                if param_dict.get("required", True):
                    result["parameters"]["required"].append(param_name)
            else:
                # Convert Pydantic model to dict excluding the required field
                param_dict = param_def.model_dump(exclude={"required"})
                # Remove any None values that can cause schema validation issues
                param_dict = {k: v for k, v in param_dict.items() if v is not None}
                # Ensure enum is never null but a list or removed entirely
                if "enum" in param_dict and param_dict["enum"] is None:
                    del param_dict["enum"]
                result["parameters"]["properties"][param_name] = param_dict
                if param_def.required:
                    result["parameters"]["required"].append(param_name)

        # Ensure parameters.required is not empty to prevent Azure OpenAI errors
        if not result["parameters"]["required"]:
            del result["parameters"]["required"]

        return result

    def invoke(self, arguments: Dict[str, Any]) -> Any:
        """
        Invoke the tool with the given arguments.

        Args:
            arguments: The arguments to pass to the tool function.

        Returns:
            The result of the tool function.

        Raises:
            ValueError: If the tool has no associated function.
        """
        if self.function is None:
            raise ValueError(f"Tool '{self.name}' has no associated function")

        return self.function(**arguments)
