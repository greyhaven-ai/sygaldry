"""
Lilypad Compatibility Layer for Mirascope v2

This module provides a compatibility layer that makes Lilypad work with Mirascope v2
by providing the old Mirascope v1 API using v2's internals.

Mirascope v1 → v2 Mapping:
- mirascope.core.base.BaseCallResponse → mirascope.llm.Response / AsyncResponse
- mirascope.core.base.BaseStream → mirascope.llm.Stream (TextStream | ToolCallStream | ThoughtStream)
- mirascope.core.base.BaseType → str | int | float | bool
- mirascope.core.base.BaseStructuredStream → (needs investigation)
- mirascope.integrations._middleware_factory.SyncFunc → Callable (sync)
- mirascope.integrations._middleware_factory.AsyncFunc → Callable (async)
"""

from __future__ import annotations

from typing import Any, Callable, Coroutine, TypeAlias, TypeVar, Protocol
from collections.abc import Awaitable

# Import Mirascope v2 types
from mirascope.llm import (
    Response,
    AsyncResponse,
    TextStream,
    ToolCallStream,
    ThoughtStream,
    AsyncTextStream,
    AsyncToolCallStream,
    AsyncThoughtStream,
)

# Type aliases for backward compatibility with Mirascope v1

# BaseCallResponse is now Response or AsyncResponse
BaseCallResponse: TypeAlias = Response | AsyncResponse

# BaseStream is now a Union of stream types
BaseStream: TypeAlias = (
    TextStream
    | ToolCallStream
    | ThoughtStream
    | AsyncTextStream
    | AsyncToolCallStream
    | AsyncThoughtStream
)

# BaseType represents basic Python types that can be returned
BaseType: TypeAlias = str | int | float | bool

# BaseStructuredStream - in v2, this is handled differently
# For now, we'll make it an alias to the stream types with format
BaseStructuredStream: TypeAlias = BaseStream

# Function type aliases for middleware
_P = TypeVar("_P")
_R = TypeVar("_R")

SyncFunc: TypeAlias = Callable[..., Any]
AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]


class MiddlewareFactoryProtocol(Protocol):
    """Protocol for middleware factory function."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Middleware factory callable."""
        ...


def middleware_factory(*args: Any, **kwargs: Any) -> Any:
    """
    Compatibility middleware factory for Lilypad.

    In Mirascope v2, middleware is handled differently.
    This provides a passthrough for now.
    """
    # TODO: Implement proper middleware factory for v2
    # For now, return a no-op middleware
    return lambda fn: fn


__all__ = [
    "BaseCallResponse",
    "BaseStream",
    "BaseType",
    "BaseStructuredStream",
    "SyncFunc",
    "AsyncFunc",
    "middleware_factory",
]
