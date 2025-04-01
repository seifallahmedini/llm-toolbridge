# Tool Classes

The Tool module provides classes for defining tools that can be used by LLMs through the LLM Tool Bridge library.

## Overview

Tools in the context of LLM function calling are functions that LLMs can invoke to perform actions or retrieve information. The `Tool` class and related types provide a structured way to define these tools, their parameters, and how they execute.

## Key Classes

### Tool

The primary class for defining tools that LLMs can call:

```python
class Tool(BaseModel):
    """
    Definition of a tool that can be used by an LLM.
    """
    name: str
    description: str
    parameters: Dict[str, Union[ParameterDefinition, Dict[str, Any]]]
    version: str = "1.0.0"
    function: Optional[Callable] = None
```

### ParameterDefinition

A structured way to define parameters for tools:

```python
class ParameterDefinition(BaseModel):
    """
    Definition of a parameter for a tool.
    """
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    enum: Optional[List[Any]] = None
    required: bool = True
    default: Optional[Any] = None
```

## Creating Tools

Tools can be defined in two ways: using dictionaries or using the `ParameterDefinition` class.

### Using Dictionaries

```python
from src.core import Tool

# Create a tool with dictionary parameters
search_tool = Tool(
    name="search",
    description="Search for information on a topic",
    parameters={
        "query": {
            "type": "string", 
            "description": "The search query"
        },
        "max_results": {
            "type": "integer", 
            "description": "Maximum number of results to return",
            "required": False,
            "default": 5
        }
    }
)
```

### Using ParameterDefinition

```python
from src.core import Tool, ParameterDefinition

# Create a tool with ParameterDefinition parameters
calculator_tool = Tool(
    name="calculator",
    description="Perform mathematical operations",
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
```

## Binding Functions to Tools

To make tools executable, bind a function to them:

```python
def search_function(query: str, max_results: int = 5):
    # Implementation would search for information
    results = [f"Result {i} for {query}" for i in range(max_results)]
    return {"query": query, "results": results}

# Assign function to the tool
search_tool.function = search_function

# Now the tool can be invoked
result = search_tool.invoke({"query": "climate change", "max_results": 3})
```

## Tool Methods

### to_dict()

Converts the tool to a dictionary format suitable for LLM providers:

```python
tool_dict = calculator_tool.to_dict()
# Returns a standardized JSON Schema format that providers understand
```

### invoke()

Executes the tool with the given arguments:

```python
def calculate(operation: str, x: float, y: float):
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Assign the function to the tool
calculator_tool.function = calculate

# Invoke the tool
result = calculator_tool.invoke({
    "operation": "multiply",
    "x": 5,
    "y": 3
})
# result will be 15
```

## Best Practices

1. **Provide clear descriptions** for tools and parameters to help the LLM understand when and how to use them.

2. **Use appropriate parameter types** that match the expected inputs.

3. **Set reasonable defaults** for optional parameters.

4. **Implement error handling** in your tool functions to gracefully handle invalid inputs.

5. **Keep tools focused** on performing a single, well-defined task rather than creating complex multi-purpose tools.

6. **Document limitations** in the tool description, such as rate limits or data constraints.

## Parameter Types

The following parameter types are supported:

- `string`: Text values
- `number`: Floating-point numbers
- `integer`: Whole numbers
- `boolean`: True/false values
- `array`: Lists of values
- `object`: Nested objects/dictionaries

## Enum Values

For parameters with a fixed set of allowed values, use the enum field:

```python
ParameterDefinition(
    type="string",
    description="Sort order",
    enum=["ascending", "descending"]
)
```

This helps guide the LLM to provide valid values for the parameter.