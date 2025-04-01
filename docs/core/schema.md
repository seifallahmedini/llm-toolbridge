# Schema Classes

The Schema module provides standardized data classes for request and response formats used throughout the LLM Tool Bridge library.

## Overview

The Schema module defines Pydantic models for:

1. Requests to the LLM Tool Bridge
2. Results from tool executions
3. Responses from the LLM Tool Bridge

These schemas ensure data consistency and validation across the library.

## Key Classes

### ToolBridgeRequest

Represents a request to the LLM Tool Bridge:

```python
class ToolBridgeRequest(BaseModel):
    """
    Base class for tool bridge requests.
    """
    prompt: str
    tools: Optional[List[Tool]] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
```

### ToolResult

Represents the result of a tool execution:

```python
class ToolResult(BaseModel):
    """
    Result of a tool execution.
    """
    tool_name: str
    call_id: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    success: bool = True
```

### ToolBridgeResponse

Represents a response from the LLM Tool Bridge:

```python
class ToolBridgeResponse(BaseModel):
    """
    Response from the tool bridge.
    """
    content: Optional[str] = None
    tool_results: List[ToolResult] = Field(default_factory=list)
    provider_name: str
    usage: Optional[Dict[str, Any]] = None
```

## Usage Examples

### Creating a Request

```python
from src.core.schema import ToolBridgeRequest
from src.core.tool import Tool

# Create a tool
calculator_tool = Tool(
    name="calculator",
    description="Performs basic calculations",
    parameters={
        "operation": {"type": "string", "description": "Operation to perform"},
        "x": {"type": "number", "description": "First operand"},
        "y": {"type": "number", "description": "Second operand"}
    }
)

# Create a request
request = ToolBridgeRequest(
    prompt="Calculate 25 * 12",
    tools=[calculator_tool],
    temperature=0.5,
    max_tokens=100
)

# Access request properties
print(request.prompt)
print(len(request.tools))
```

### Working with Tool Results

```python
from src.core.schema import ToolResult

# Create a successful tool result
success_result = ToolResult(
    tool_name="calculator",
    call_id="call_123",
    result=30,
    success=True
)

# Create an error tool result
error_result = ToolResult(
    tool_name="weather",
    call_id="call_456",
    error="API rate limit exceeded",
    success=False
)
```

### Creating a Response

```python
from src.core.schema import ToolBridgeResponse, ToolResult

# Create tool results
calc_result = ToolResult(
    tool_name="calculator",
    call_id="call_123",
    result=30,
    success=True
)

# Create a response
response = ToolBridgeResponse(
    content="The result of the calculation is 30.",
    tool_results=[calc_result],
    provider_name="azure_openai",
    usage={"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35}
)

# Access response properties
print(response.content)
for result in response.tool_results:
    print(f"{result.tool_name}: {result.result}")
```

## Schema Validation

All schema classes are built on Pydantic, which provides automatic data validation:

```python
# This will raise a validation error because prompt is required
try:
    invalid_request = ToolBridgeRequest()
except Exception as e:
    print(f"Validation error: {e}")

# This will raise a validation error due to invalid temperature
try:
    invalid_request = ToolBridgeRequest(
        prompt="Hello",
        temperature=2.0  # Temperature should be between 0 and 1
    )
except Exception as e:
    print(f"Validation error: {e}")
```

## Schema Extensions

The schema classes can be extended to add provider-specific fields:

```python
from pydantic import BaseModel, Field
from src.core.schema import ToolBridgeRequest

class AzureOpenAIRequest(ToolBridgeRequest):
    """Azure OpenAI specific request parameters."""
    api_version: str = "2023-12-01-preview"
    deployment_name: str
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
```

## Serialization and Deserialization

Schema classes can be easily serialized to JSON and deserialized:

```python
import json
from src.core.schema import ToolBridgeResponse

# Create a response
response = ToolBridgeResponse(
    content="Hello, world!",
    provider_name="azure_openai"
)

# Serialize to JSON
json_str = response.model_dump_json()
print(json_str)

# Deserialize from JSON
data = json.loads(json_str)
new_response = ToolBridgeResponse(**data)
print(new_response.content)
```

## Best Practices

1. **Validate input data** using schema classes before processing.

2. **Handle validation errors** gracefully to provide meaningful feedback.

3. **Use typed fields** to ensure type safety and enable IDE auto-completion.

4. **Extend base schemas** for provider-specific requirements rather than creating entirely new schemas.

5. **Include all necessary metadata** in responses to aid in debugging and monitoring.