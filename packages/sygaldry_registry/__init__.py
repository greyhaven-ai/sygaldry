"""
Sygaldry Registry - Component registry for AI agents and tools.

Automatically applies Lilypad-Mirascope v2 compatibility patch.
"""

# Auto-apply Lilypad compatibility patch for Mirascope v2
try:
    from sygaldry.lilypad_compat import patch

    if not patch.is_applied():
        patch.apply()
except ImportError:
    # Compatibility patch not available, continue without it
    pass

__version__ = "0.1.0"
