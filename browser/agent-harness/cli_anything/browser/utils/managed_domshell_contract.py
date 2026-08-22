"""Shared names and error type for the managed DOMShell runtime."""

from __future__ import annotations


DOMSHELL_EXTENSION_ENV = "CLI_ANYTHING_DOMSHELL_EXTENSION_DIR"
AGENT_BROWSER_SESSION = "cabsec"
AGENT_BROWSER_NAMESPACE = "cabsec"


class ManagedDOMShellError(RuntimeError):
    """A managed Chrome/DOMShell session cannot be safely established."""
