"""Security utilities for browser automation.

This module provides security functions for the DOMShell MCP browser harness,
including URL validation, DOM content sanitization, and attack surface mitigation.

Threat Model:
- SSRF: Browser can access arbitrary URLs including localhost/private networks
- DOM-based prompt injection: Malicious ARIA labels can manipulate agent behavior
- Scheme injection: javascript:, file:, data: URLs can execute code locally
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from cli_anything.browser.utils._net_guard import host_is_private
from cli_anything.browser.utils.dom_sanitize import sanitize_dom_text

__all__ = [
    "validate_url",
    "sanitize_dom_text",
    "is_private_network_blocked",
    "get_allowed_schemes",
    "get_blocked_schemes",
]


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("true", "1", "yes", "on")


# Private/loopback networks are blocked BY DEFAULT (the harness threat model is a
# prompt-injected agent). Opt out for local development with
# CLI_ANYTHING_BROWSER_ALLOW_PRIVATE=1; the legacy *_BLOCK_PRIVATE=0 override is
# also honored so existing dev setups keep working.
_BLOCK_PRIVATE_NETWORKS = _env_flag("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", True) and not _env_flag(
    "CLI_ANYTHING_BROWSER_ALLOW_PRIVATE", False
)

# Allowed URL schemes (comma-separated env override), normalized to lowercase.
_ALLOWED_SCHEMES = {
    scheme
    for scheme in (
        s.strip().lower()
        for s in os.environ.get("CLI_ANYTHING_BROWSER_ALLOWED_SCHEMES", "http,https").split(",")
    )
    if scheme
}

# Dangerous URI schemes that should NEVER be allowed.
_BLOCKED_SCHEMES = {
    "file",              # Local file access
    "javascript",        # Code execution
    "data",              # Data URI attacks
    "vbscript",          # Legacy IE script injection
    "about",             # Browser-internal pages
    "chrome",            # Chrome internal pages
    "chrome-extension",  # Chrome extensions
    "moz-extension",     # Firefox extensions
    "edge",              # Edge internal pages
    "safari",            # Safari internal pages
    "opera",             # Opera internal pages
    "brave",             # Brave internal pages
}


def validate_url(url: str) -> tuple[bool, str]:
    """Validate a URL for security.

    Checks, in order:
    1. Dangerous URI schemes (file://, javascript://, ...).
    2. An explicit, allowed scheme (http/https by default).
    3. A hostname is present.
    4. Private/loopback network access (resolved via ipaddress + DNS), when
       blocking is enabled (the default).

    Returns ``(is_valid, error_message)``; ``(True, "")`` when the URL is valid.

    Examples:
        >>> validate_url("https://example.com")
        (True, "")
        >>> validate_url("file:///etc/passwd")
        (False, "Blocked URL scheme: file")
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    url = url.strip()
    if not url:
        return False, "URL cannot be empty or whitespace"

    try:
        parsed = urlparse(url)
    except Exception as e:  # noqa: BLE001 - report any parse failure as invalid
        return False, f"Invalid URL: {e}"

    scheme = parsed.scheme.lower()
    if scheme in _BLOCKED_SCHEMES:
        return False, f"Blocked URL scheme: {scheme}"
    if not scheme:
        return False, f"URL must include an explicit scheme. Allowed: {', '.join(sorted(_ALLOWED_SCHEMES))}"
    if scheme not in _ALLOWED_SCHEMES:
        return False, f"Unsupported URL scheme: {scheme}. Allowed: {', '.join(sorted(_ALLOWED_SCHEMES))}"

    hostname = parsed.hostname or ""
    if not hostname:
        return False, "URL must include a hostname"

    if _BLOCK_PRIVATE_NETWORKS and host_is_private(hostname):
        return False, f"Private network access blocked: {hostname}"

    return True, ""


def is_private_network_blocked() -> bool:
    """True if localhost / private-IP access is blocked (default: True)."""
    return _BLOCK_PRIVATE_NETWORKS


def get_allowed_schemes() -> set[str]:
    """Return a copy of the allowed URL schemes (e.g. {"http", "https"})."""
    return _ALLOWED_SCHEMES.copy()


def get_blocked_schemes() -> set[str]:
    """Return a copy of the always-blocked URL schemes."""
    return _BLOCKED_SCHEMES.copy()
