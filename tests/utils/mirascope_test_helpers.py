"""Test helpers specifically for Mirascope v2-based components following best practices."""

import asyncio
import pytest
from collections.abc import Callable
from pydantic import BaseModel, ValidationError
from tenacity import RetryError
from typing import Any, TypeVar
from unittest.mock import AsyncMock, Mock, patch

T = TypeVar("T", bound=BaseModel)

# Note: Mirascope v2 uses different internal structures than v1
# Many v1 test helpers need to be adapted or removed


class MirascopeTestHelper:
    """Helper utilities for testing Mirascope components."""

    @staticmethod
    def assert_uses_llm_decorator(func: Callable) -> None:
        """Assert that a function uses the @llm.call decorator.
        
        Args:
            func: Function to check
            
        Raises:
            AssertionError: If function doesn't use @llm.call
        """
        # Check for Mirascope decorator attributes
        assert hasattr(func, "__wrapped__"), "Function should use @llm.call decorator"
        
        # Look for Mirascope-specific attributes
        wrapped = func
        found_llm_call = False
        
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                found_llm_call = True
                break
            wrapped = wrapped.__wrapped__
        
        assert found_llm_call, "Function must use @llm.call decorator"

    @staticmethod
    def assert_returns_prompt_string(func: Callable) -> None:
        """Assert that a function returns a prompt string (v2 functional prompt pattern).

        In Mirascope v2, prompt templates are replaced with functions that return
        formatted strings.

        Args:
            func: Function to check

        Raises:
            AssertionError: If function doesn't return a string
        """
        import inspect

        # Check return annotation
        sig = inspect.signature(func)
        assert sig.return_annotation == str or sig.return_annotation == "str", \
            "Function should return str for v2 functional prompts"

        # For wrapped functions, check the inner function
        if hasattr(func, "__wrapped__"):
            inner_func = func.__wrapped__
            if hasattr(inner_func, "__annotations__"):
                assert inner_func.__annotations__.get("return") == str, \
                    "Inner function should return str"

    @staticmethod
    def assert_has_format_model(func: Callable, model_class: type[BaseModel]) -> None:
        """Assert that a function uses a specific format model (v2 'format' parameter).

        In Mirascope v2, 'response_model' is renamed to 'format'.

        Args:
            func: Function to check
            model_class: Expected format model class

        Raises:
            AssertionError: If function doesn't use the expected format model
        """
        # In v2, format configuration might be stored differently
        # For now, we'll check the function signature and decorator usage
        import inspect

        # Try to get decorator kwargs if available
        wrapped = func
        while hasattr(wrapped, "__wrapped__"):
            # Check for v2-style attributes (may vary by Mirascope v2 implementation)
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                format_model = wrapped._mirascope_call_kwargs.get("format")
                assert format_model is model_class, \
                    f"Expected format {model_class.__name__}, got {format_model}"
                return
            wrapped = wrapped.__wrapped__

        # If we can't find the decorator kwargs, at least verify it's decorated
        assert hasattr(func, "__wrapped__"), "Function should use @llm.call decorator"

    @staticmethod
    def assert_has_provider_config(func: Callable, expected_provider: str | None = None) -> None:
        """Assert that a function has provider configuration.

        In Mirascope v2, providers are specified directly in @llm.call decorator.

        Args:
            func: Function to check
            expected_provider: Optional expected provider string (e.g., "openai:completions")

        Raises:
            AssertionError: If function doesn't have provider configured
        """
        wrapped = func
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                provider = wrapped._mirascope_call_kwargs.get("provider", "")

                assert provider, "Function should have a provider configured"

                if expected_provider:
                    assert provider == expected_provider, \
                        f"Expected provider '{expected_provider}', got '{provider}'"
                return
            wrapped = wrapped.__wrapped__

        raise AssertionError("Function doesn't have provider configuration")

    @staticmethod
    def get_mirascope_config(func: Callable) -> dict[str, Any]:
        """Extract Mirascope configuration from a decorated function.
        
        Args:
            func: Decorated function
            
        Returns:
            Dictionary of Mirascope configuration
        """
        config = {}
        wrapped = func
        
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                config.update(wrapped._mirascope_call_kwargs)
                break
            wrapped = wrapped.__wrapped__
        
        return config

    @staticmethod
    def create_mock_message(content: str, role: str = "assistant") -> Mock:
        """Create a mock message for testing.

        Args:
            content: Message content
            role: Message role (user, assistant, system)

        Returns:
            Mock message object
        """
        mock = Mock()
        mock.content = content
        mock.role = role
        return mock

    @staticmethod
    def create_mock_tool_response(
        tool_name: str,
        result: Any,
        success: bool = True
    ) -> Mock:
        """Create a mock tool response.
        
        Args:
            tool_name: Name of the tool
            result: Tool result
            success: Whether the tool call succeeded
            
        Returns:
            Mock tool response
        """
        response = Mock()
        response.tool_name = tool_name
        response.result = result
        response.success = success
        response.error = None if success else "Tool execution failed"
        return response


class MirascopeMockFactory:
    """Factory for creating Mirascope-specific mocks."""

    @staticmethod
    def mock_llm_call(
        provider: str = "openai:completions",
        model_id: str = "gpt-4o-mini",
        response_content: str = "Mock response",
        format_model: type[BaseModel] | None = None,
        response_data: BaseModel | None = None,
        stream: bool = False
    ):
        """Create a context manager that mocks @llm.call decorated functions.

        Updated for Mirascope v2 with format (not response_model) and model_id (not model).

        Args:
            provider: Provider to mock (e.g., "openai:completions")
            model_id: Model ID to mock (e.g., "gpt-4o-mini")
            response_content: Text content of response
            format_model: Expected format model class (v2 replaces response_model)
            response_data: Structured response data
            stream: Whether to mock streaming

        Returns:
            Context manager for mocking
        """
        def mock_decorator(func):
            if stream:
                # Create streaming mock
                async def async_gen():
                    words = response_content.split()
                    for word in words:
                        yield Mock(content=word + " ")

                return AsyncMock(return_value=async_gen())

            # Create regular mock
            mock_response = Mock()
            mock_response.content = response_content
            mock_response.model_id = model_id

            if format_model and response_data:
                mock_response.parsed = response_data
            elif format_model:
                # Auto-generate mock data
                mock_response.parsed = MirascopeMockFactory._generate_mock_model(format_model)

            if asyncio.iscoroutinefunction(func):
                return AsyncMock(return_value=mock_response)
            return Mock(return_value=mock_response)

        # In v2, provider format is "provider:api_type", so we need to handle it differently
        provider_name = provider.split(":")[0] if ":" in provider else provider
        return patch(f"mirascope.{provider_name}.{provider_name}.call", side_effect=mock_decorator)

    @staticmethod
    def _generate_mock_model(model_class: type[BaseModel]) -> BaseModel:
        """Generate a mock instance of a Pydantic model.
        
        Args:
            model_class: The model class to instantiate
            
        Returns:
            Mock instance with default values
        """
        mock_data: dict[str, Any] = {}
        
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            
            # Generate appropriate mock values based on type
            if field_type is str:
                mock_data[field_name] = f"mock_{field_name}"
            elif field_type is int:
                mock_data[field_name] = 42
            elif field_type is float:
                mock_data[field_name] = 0.95
            elif field_type is bool:
                mock_data[field_name] = True
            elif field_type is not None and hasattr(field_type, "__origin__"):
                if field_type.__origin__ is list:
                    mock_data[field_name] = ["item1", "item2"]
                elif field_type.__origin__ is dict:
                    mock_data[field_name] = {"key": "value"}
            else:
                # For complex types, try None if optional
                if not field_info.is_required():
                    mock_data[field_name] = None
        
        return model_class(**mock_data)

    @staticmethod
    def mock_tool_call(
        tool_func: Callable,
        return_value: Any = "Mock tool result",
        side_effect: Exception | None = None
    ):
        """Mock a tool function call.
        
        Args:
            tool_func: Tool function to mock
            return_value: Value to return
            side_effect: Exception to raise
            
        Returns:
            Mock patch object
        """
        if side_effect:
            return patch.object(
                tool_func,
                "__call__",
                side_effect=side_effect
            )
        
        return patch.object(
            tool_func,
            "__call__",
            return_value=return_value
        )


class MirascopeTestCase:
    """Base test case for Mirascope components following best practices."""

    @pytest.mark.asyncio
    async def test_retry_behavior(
        self,
        func_with_retry: Callable,
        mock_failure_count: int = 2
    ):
        """Test retry behavior with Tenacity.
        
        Args:
            func_with_retry: Function decorated with @retry
            mock_failure_count: Number of failures before success
        """
        call_count = 0
        
        async def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= mock_failure_count:
                raise ValidationError("Mock validation error")
            
            return Mock(content="Success after retries")
        
        with patch("mirascope.llm.call", side_effect=mock_response):
            result = await func_with_retry("test input")
            
            assert call_count == mock_failure_count + 1
            assert result.content == "Success after retries"

    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self,
        func_with_response_model: Callable,
        invalid_response_data: dict[str, Any]
    ):
        """Test handling of Pydantic validation errors.
        
        Args:
            func_with_response_model: Function with response_model
            invalid_response_data: Data that should fail validation
        """
        mock_response = Mock()
        mock_response.parsed = invalid_response_data
        
        with patch("mirascope.llm.call", return_value=mock_response):
            with pytest.raises(ValidationError) as exc_info:
                await func_with_response_model("test input")
            
            assert "validation error" in str(exc_info.value).lower()

    def test_tool_error_handling(
        self,
        agent_with_tools: Callable,
        tool_error: Exception
    ):
        """Test agent behavior when tools fail.
        
        Args:
            agent_with_tools: Agent that uses tools
            tool_error: Exception to raise from tool
        """
        # Mock the tool to raise an error
        with patch("tool_function", side_effect=tool_error):
            # Agent should handle tool errors gracefully
            result = agent_with_tools("test query")
            
            # Check that error is handled
            assert "error" in result.lower() or hasattr(result, "error")


# Pytest fixtures for Mirascope testing
@pytest.fixture
def mock_mirascope_response():
    """Create a mock Mirascope v2 response."""
    def _create_response(
        content: str = "Mock response",
        provider: str = "openai:completions",
        model_id: str = "gpt-4o-mini",
        **kwargs
    ):
        response = Mock()
        response.content = content
        response.provider = provider
        response.model_id = model_id

        for key, value in kwargs.items():
            setattr(response, key, value)

        return response

    return _create_response


@pytest.fixture
def mock_structured_response():
    """Create a mock structured response with Pydantic model."""
    def _create_response(
        model_class: type[BaseModel],
        data: dict[str, Any] | None = None
    ):
        if data:
            return model_class(**data)
        return MirascopeMockFactory._generate_mock_model(model_class)
    
    return _create_response


@pytest.fixture
def assert_mirascope_best_practices():
    """Fixture that provides assertions for Mirascope best practices."""
    return MirascopeTestHelper
