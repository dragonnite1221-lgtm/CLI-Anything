# ruff: noqa: F403, F405, E501
"""Security module tests.

Tests URL validation, DOM sanitization, and security utilities.
These tests don't require DOMShell backend.
"""

import importlib
import os
import pytest
from cli_anything.browser.utils import security


def _reload_security_module():
    """Reload the security module to pick up env var changes."""
    importlib.reload(security)


_reload_security_module()
from cli_anything.browser.utils.security import (
    get_allowed_schemes,
    get_blocked_schemes,
    is_private_network_blocked,
    sanitize_dom_text,
    validate_url,
)


__all__ = [
    "_reload_security_module",
    "get_allowed_schemes",
    "get_blocked_schemes",
    "importlib",
    "is_private_network_blocked",
    "os",
    "pytest",
    "sanitize_dom_text",
    "security",
    "validate_url",
]
