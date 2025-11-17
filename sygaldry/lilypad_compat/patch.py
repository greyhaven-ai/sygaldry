"""
Monkey-patch Lilypad to work with Mirascope v2.

This module patches Lilypad's imports to use our compatibility layer
instead of the non-existent Mirascope v1 modules.

Usage:
    Import this module BEFORE importing lilypad:

    ```python
    from sygaldry.lilypad_compat import patch
    patch.apply()

    # Now lilypad will work with Mirascope v2
    from lilypad import trace
    ```
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any


def _create_mirascope_core_module() -> ModuleType:
    """Create a fake mirascope.core module for Lilypad."""
    mirascope_core = ModuleType("mirascope.core")
    return mirascope_core


def _create_mirascope_core_base_module() -> ModuleType:
    """Create a fake mirascope.core.base module with v1 API using v2 types."""
    from . import (
        BaseCallResponse,
        BaseStream,
        BaseType,
        BaseStructuredStream,
    )

    base_module = ModuleType("mirascope.core.base")

    # Add the compatibility types to the fake module
    base_module.BaseCallResponse = BaseCallResponse  # type: ignore
    base_module.BaseStream = BaseStream  # type: ignore
    base_module.BaseType = BaseType  # type: ignore
    base_module.BaseStructuredStream = BaseStructuredStream  # type: ignore

    return base_module


def _create_mirascope_integrations_module() -> ModuleType:
    """Create a fake mirascope.integrations module."""
    integrations = ModuleType("mirascope.integrations")
    return integrations


def _create_middleware_factory_module() -> ModuleType:
    """Create a fake mirascope.integrations._middleware_factory module."""
    from . import SyncFunc, AsyncFunc, middleware_factory

    middleware_module = ModuleType("mirascope.integrations._middleware_factory")

    # Add the types and factory
    middleware_module.SyncFunc = SyncFunc  # type: ignore
    middleware_module.AsyncFunc = AsyncFunc  # type: ignore
    middleware_module.middleware_factory = middleware_factory  # type: ignore

    return middleware_module


def _create_base_utils_module() -> ModuleType:
    """Create a fake mirascope.core.base._utils module."""
    import inspect
    from typing import Callable

    utils_module = ModuleType("mirascope.core.base._utils")

    # fn_is_async function - checks if a function is async
    def fn_is_async(fn: Callable) -> bool:
        """Check if a function is async."""
        return inspect.iscoroutinefunction(fn)

    utils_module.fn_is_async = fn_is_async  # type: ignore

    return utils_module


def _create_base_type_module() -> ModuleType:
    """Create a fake mirascope.core.base._utils._base_type module."""
    from . import BaseType

    base_type_module = ModuleType("mirascope.core.base._utils._base_type")
    base_type_module.BaseType = BaseType  # type: ignore

    return base_type_module


def _create_stream_module() -> ModuleType:
    """Create a fake mirascope.core.base.stream module."""
    from . import BaseStream

    stream_module = ModuleType("mirascope.core.base.stream")
    stream_module.BaseStream = BaseStream  # type: ignore

    return stream_module


def _create_call_response_module() -> ModuleType:
    """Create a fake mirascope.core.base.call_response module."""
    from . import BaseCallResponse

    call_response_module = ModuleType("mirascope.core.base.call_response")
    call_response_module.BaseCallResponse = BaseCallResponse  # type: ignore

    return call_response_module


def _create_structured_stream_module() -> ModuleType:
    """Create a fake mirascope.core.base.structured_stream module."""
    from . import BaseStructuredStream

    structured_stream_module = ModuleType("mirascope.core.base.structured_stream")
    structured_stream_module.BaseStructuredStream = BaseStructuredStream  # type: ignore

    return structured_stream_module


def apply() -> None:
    """
    Apply the Lilypad compatibility patch.

    This function monkey-patches the import system to provide
    Mirascope v1 modules using v2 types.

    Call this BEFORE importing lilypad.
    """
    # Check if mirascope.core exists (it shouldn't in v2)
    if "mirascope.core" in sys.modules:
        # Already patched or using v1
        return

    # Create the fake modules
    mirascope_core = _create_mirascope_core_module()
    mirascope_core_base = _create_mirascope_core_base_module()
    mirascope_integrations = _create_mirascope_integrations_module()
    middleware_factory_module = _create_middleware_factory_module()
    base_utils_module = _create_base_utils_module()
    base_type_module = _create_base_type_module()
    stream_module = _create_stream_module()
    call_response_module = _create_call_response_module()
    structured_stream_module = _create_structured_stream_module()

    # Inject them into sys.modules so imports will find them
    sys.modules["mirascope.core"] = mirascope_core
    sys.modules["mirascope.core.base"] = mirascope_core_base
    sys.modules["mirascope.core.base._utils"] = base_utils_module
    sys.modules["mirascope.core.base._utils._base_type"] = base_type_module
    sys.modules["mirascope.core.base.stream"] = stream_module
    sys.modules["mirascope.core.base.call_response"] = call_response_module
    sys.modules["mirascope.core.base.structured_stream"] = structured_stream_module
    sys.modules["mirascope.integrations"] = mirascope_integrations
    sys.modules["mirascope.integrations._middleware_factory"] = middleware_factory_module

    # Set the base module as an attribute of core (for `from mirascope.core import base`)
    mirascope_core.base = mirascope_core_base  # type: ignore
    mirascope_core_base._utils = base_utils_module  # type: ignore

    print("✓ Lilypad compatibility patch applied successfully")


def is_applied() -> bool:
    """Check if the patch has been applied."""
    return "mirascope.core" in sys.modules


__all__ = ["apply", "is_applied"]
