"""
Google Gemini Adapter module.

This module provides the adapter implementation for the Google Gemini provider,
allowing it to be used with the standard ToolBridge interface.
"""

from typing import Any, Dict, List, Optional

from ..core.adapter import BaseProviderAdapter, ProviderCapabilities
from ..core.provider import Provider, LLMResponse
from ..core.tool import Tool
from ..providers.gemini import GeminiProvider


class GeminiAdapter(BaseProviderAdapter[Dict[str, Any], Any]):
    """
    Adapter implementation for the Google Gemini provider.
    
    This adapter translates between the standard ToolBridge interface
    and the specific implementation details of the Google Gemini API.
    """
    
    def __init__(self, provider: Provider):
        """
        Initialize the adapter with a Gemini provider.
        
        Args:
            provider: The Gemini provider instance to adapt.
            
        Raises:
            TypeError: If the provided provider is not a GeminiProvider.
        """
        if not isinstance(provider, GeminiProvider):
            raise TypeError("GeminiAdapter requires a GeminiProvider instance")
        
        self.provider = provider
    
    def get_capabilities(self) -> ProviderCapabilities:
        """
        Get the capabilities of the Gemini provider.
        
        Returns:
            A ProviderCapabilities object describing what the provider can do.
        """
        return ProviderCapabilities(
            supports_tool_calling=True,
            supports_multiple_tools=True,
            supports_streaming=False,  # Gemini does support streaming, but not implemented in this adapter yet
            supports_vision=True,      # Gemini models support vision inputs
            max_tokens_limit=32768     # Gemini 1.5 Pro supports very long contexts
        )
    
    def prepare_request(
        self,
        prompt: str,
        tools: Optional[List[Tool]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare a provider-specific request object.
        
        Args:
            prompt: The prompt to send to the LLM.
            tools: Optional list of tools to make available to the LLM.
            tool_results: Optional dictionary of results from previously called tools.
            **kwargs: Additional parameters for the request.
            
        Returns:
            A dictionary containing the request parameters for the Gemini provider.
        """
        # For Gemini, we'll structure the request as a dictionary
        # with the parameters expected by the provider
        request = {
            "prompt": prompt,
            "tools": tools,
            "tool_results": tool_results
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            request[key] = value
            
        return request
    
    def execute_request(self, request: Dict[str, Any]) -> Any:
        """
        Execute a prepared request using the provider.
        
        Args:
            request: The provider-specific request to execute.
            
        Returns:
            The raw response from the Gemini provider.
            
        Raises:
            Exception: If there's an error executing the request.
        """
        # Extract parameters from the request dictionary
        prompt = request.pop("prompt")
        tools = request.pop("tools", None)
        tool_results = request.pop("tool_results", None)
        
        # Call the provider's generate method (synchronous version for simplicity)
        return self.provider._generate_sync(
            prompt=prompt,
            tools=tools,
            tool_results=tool_results,
            **request
        )
    
    def parse_response(self, response: Any) -> LLMResponse:
        """
        Parse a provider-specific response into our standard format.
        
        The Gemini provider already returns responses in our LLMResponse format,
        so we can just pass it through.
        
        Args:
            response: The provider-specific response to parse.
            
        Returns:
            A standardized LLMResponse object.
        """
        # The response from GeminiProvider is already in LLMResponse format
        return response