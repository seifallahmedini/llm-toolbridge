"""
Unit tests for the AdapterRegistry class in adapter_registry.py.
"""

import pytest
from llm_toolbridge.core.adapter_registry import AdapterRegistry
from llm_toolbridge.core.adapter import BaseProviderAdapter
from llm_toolbridge.core.provider import Provider, ProviderConfig


class DummyProvider(Provider):
    def __init__(self, config: ProviderConfig):
        self.config = config

    async def generate(self, prompt, tools=None, tool_results=None, **kwargs):
        pass

    def format_tools_for_provider(self, tools):
        return []

    def parse_tool_calls(self, raw_response):
        return []


class DummyAdapter(BaseProviderAdapter):
    def __init__(self, provider: Provider):
        self.provider = provider

    def execute_request(self, *args, **kwargs):
        """
        Dummy execute_request implementation.
        """
        return None

    def get_capabilities(self) -> list:
        """
        Dummy get_capabilities implementation.
        """
        return []

    def parse_response(self, response):
        """
        Dummy parse_response implementation.
        """
        return None

    def prepare_request(self, *args, **kwargs):
        """
        Dummy prepare_request implementation.
        """
        return None


@pytest.fixture(autouse=True)
def clear_registry():
    # Clear registry before each test to avoid cross-test pollution
    AdapterRegistry._registry.clear()
    yield
    AdapterRegistry._registry.clear()


def test_register_and_get_adapter_class():
    """
    Test registering and retrieving an adapter class.
    """
    AdapterRegistry.register("dummy", DummyAdapter)
    assert AdapterRegistry.get_adapter_class("dummy") is DummyAdapter


def test_register_duplicate_provider_raises():
    """
    Test registering the same provider twice raises ValueError.
    """
    AdapterRegistry.register("dummy", DummyAdapter)
    with pytest.raises(ValueError):
        AdapterRegistry.register("dummy", DummyAdapter)


def test_get_adapter_class_unregistered_provider():
    """
    Test getting an adapter class for an unregistered provider raises KeyError.
    """
    with pytest.raises(KeyError):
        AdapterRegistry.get_adapter_class("not_registered")


def test_create_adapter_expected_use():
    """
    Test creating an adapter instance for a registered provider.
    """
    AdapterRegistry.register("dummy", DummyAdapter)
    provider = DummyProvider(ProviderConfig())
    adapter = AdapterRegistry.create_adapter("dummy", provider)
    assert isinstance(adapter, DummyAdapter)
    assert adapter.provider is provider


def test_create_adapter_unregistered_provider():
    """
    Test creating an adapter for an unregistered provider raises KeyError.
    """
    provider = DummyProvider(ProviderConfig())
    with pytest.raises(KeyError):
        AdapterRegistry.create_adapter("not_registered", provider)


def test_get_available_providers_edge_case():
    """
    Test get_available_providers returns correct mapping.
    """
    AdapterRegistry.register("dummy", DummyAdapter)
    providers = AdapterRegistry.get_available_providers()
    assert "dummy" in providers
    assert providers["dummy"] is DummyAdapter
