"""
Tool Bridge module.

This module provides the main ToolBridge class that serves as the primary
interface for interacting with LLM providers and tools.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import asyncio

from src.core.provider import Provider, LLMResponse, ToolCall
from src.core.tool import Tool


class ToolBridge:
    """
    Main interface for working with LLM tools across different providers.
    
    This class serves as the central point of interaction for users of
    the library, handling the communication between tools and LLM providers.
    """
    
    def __init__(self, provider: Provider):
        """
        Initialize the ToolBridge with a provider.
        
        Args:
            provider: The LLM provider to use for generating responses.
        """
        self.provider = provider
        self.tools: Dict[str, Tool] = {}
        
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the ToolBridge.
        
        Args:
            tool: The tool to register.
            
        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered")
            
        self.tools[tool.name] = tool
        
    def register_tools(self, tools: List[Tool]) -> None:
        """
        Register multiple tools with the ToolBridge.
        
        Args:
            tools: The tools to register.
            
        Raises:
            ValueError: If any tool with the same name is already registered.
        """
        for tool in tools:
            self.register_tool(tool)
            
    def get_tool(self, name: str) -> Tool:
        """
        Get a registered tool by name.
        
        Args:
            name: The name of the tool to retrieve.
            
        Returns:
            The requested tool.
            
        Raises:
            KeyError: If no tool with the given name is registered.
        """
        if name not in self.tools:
            raise KeyError(f"No tool with name '{name}' is registered")
            
        return self.tools[name]
        
    async def execute(
        self, 
        prompt: str, 
        tools: Optional[List[Union[Tool, str]]] = None,
        max_tool_calls: int = 10
    ) -> LLMResponse:
        """
        Execute the LLM with the given prompt and tools.
        
        This method handles the full conversation flow, including any
        tool calls that may be requested by the LLM.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
                   Can be Tool objects or names of registered tools.
            max_tool_calls: Maximum number of tool calls to allow before 
                           returning the response to avoid infinite loops.
                           
        Returns:
            The final LLM response.
        """
        # Resolve tool names to actual tool objects
        resolved_tools = self._resolve_tools(tools)
        
        # Initial generation
        response = await self.provider.generate(prompt=prompt, tools=resolved_tools)
        
        # Handle tool calls, if any
        tool_results = {}
        call_count = 0
        
        while response.tool_calls and call_count < max_tool_calls:
            call_count += 1
            
            for tool_call in response.tool_calls:
                try:
                    # Get the tool and execute it
                    tool = self.get_tool(tool_call.tool_name)
                    result = tool.invoke(tool_call.arguments)
                    
                    # Store the result
                    tool_results[tool_call.call_id or tool_call.tool_name] = result
                except Exception as e:
                    # Handle tool execution errors
                    tool_results[tool_call.call_id or tool_call.tool_name] = {
                        "error": str(e),
                        "success": False
                    }
                    
            # Generate a new response with the tool results
            response = await self.provider.generate(
                prompt=prompt,
                tools=resolved_tools,
                tool_results=tool_results
            )
            
        return response
    
    def _resolve_tools(self, tools: Optional[List[Union[Tool, str]]] = None) -> List[Tool]:
        """
        Resolve a list of tool identifiers to actual tool objects.
        
        Args:
            tools: List of tools or tool names.
            
        Returns:
            List of resolved Tool objects.
            
        Raises:
            KeyError: If a tool name is not found in registered tools.
            TypeError: If an invalid tool type is provided.
        """
        if tools is None:
            # If no tools provided, use all registered tools
            return list(self.tools.values())
            
        resolved: List[Tool] = []
        for tool in tools:
            if isinstance(tool, Tool):
                resolved.append(tool)
            elif isinstance(tool, str):
                resolved.append(self.get_tool(tool))
            else:
                raise TypeError(f"Expected Tool or str, got {type(tool).__name__}")
                
        return resolved
    
    def execute_sync(
        self, 
        prompt: str, 
        tools: Optional[List[Union[Tool, str]]] = None,
        max_tool_calls: int = 10
    ) -> LLMResponse:
        """
        Synchronous version of execute.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            max_tool_calls: Maximum number of tool calls to allow.
            
        Returns:
            The final LLM response.
        """
        return asyncio.run(self.execute(prompt, tools, max_tool_calls))