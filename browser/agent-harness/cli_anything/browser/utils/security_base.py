# ruff: noqa: E501
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
import re
from urllib.parse import urlparse


# Environment variable to control private network blocking
# Default: False (allow localhost/private networks for development)
# Set to "true" or "1" in production to enable blocking
_BLOCK_PRIVATE_NETWORKS = os.environ.get(
    "CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", ""
).lower() in ("true", "1")

# Environment variable to define allowed URL schemes (comma-separated)
# Default: "http,https"
# Normalized to lowercase and empty entries filtered
_ALLOWED_SCHEMES = set(
    scheme
    for scheme in (
        s.strip().lower()
        for s in os.environ.get(
            "CLI_ANYTHING_BROWSER_ALLOWED_SCHEMES", "http,https"
        ).split(",")
    )
    if scheme
)

# Dangerous URI schemes that should NEVER be allowed
_BLOCKED_SCHEMES = {
    "file",  # Local file access
    "javascript",  # Code execution
    "data",  # Data URI attacks
    "vbscript",  # Legacy IE script injection
    "about",  # Browser-internal pages
    "chrome",  # Chrome internal pages
    "chrome-extension",  # Chrome extensions
    "moz-extension",  # Firefox extensions
    "edge",  # Edge internal pages
    "safari",  # Safari internal pages
    "opera",  # Opera internal pages
    "brave",  # Brave internal pages
}

# Private network patterns (RFC 1918 + loopback + link-local)
# These patterns match localhost and private IP ranges
_PRIVATE_NETWORK_PATTERNS = [
    r"^127\.\d+\.\d+\.\d+",  # 127.0.0.0/8 (loopback)
    r"^::1$",  # IPv6 loopback
    r"^localhost$",  # localhost hostname
    r"^localhost:",  # localhost with port
    r"^0\.0\.0\.0$",  # 0.0.0.0 (all interfaces)
    r"^10\.\d+\.\d+\.\d+",  # 10.0.0.0/8 (private Class A)
    r"^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+",  # 172.16.0.0/12 (private Class B)
    r"^192\.168\.\d+\.\d+",  # 192.168.0.0/16 (private Class C)
    r"^169\.254\.\d+\.\d+",  # 169.254.0.0/16 (link-local)
    r"^fc00:",  # IPv6 unique local (ULA)
    r"^fd[0-9a-f]{2}:",  # IPv6 unique local (ULA) prefix - fixed to require hex + colon
    r"^fe80:",  # IPv6 link-local
    r"^::",  # IPv6 unspecified/loopback variants
    r"^\[::1\]",  # IPv6 loopback with brackets
    r"^\[::\]",  # IPv6 unspecified with brackets
    r"^\[fe80:",  # IPv6 link-local with brackets
    r"^\[fd[0-9a-f]{2}:",  # IPv6 unique local (ULA) prefix with brackets
]

# Suspicious patterns that may indicate prompt injection attempts
# These patterns are commonly used in prompt injection attacks
_PROMPT_INJECTION_PATTERNS = [
    "ignore previous",
    "forget",
    "disregard",
    "ignore all",
    "system prompt",
    "新的指令",  # Chinese: "new instructions"
    "ignorar anteriores",  # Spanish: "ignore previous"
    "ignorar tudo",  # Portuguese: "ignore everything"
    "无视之前的",  # Chinese: "disregard previous"
    "不要理会",  # Chinese: "don't pay attention to"
    "<!--",  # HTML comment start (could hide instructions)
    "<script",  # Script tag (potential XSS)
]

__all__ = [
    "_ALLOWED_SCHEMES",
    "_BLOCKED_SCHEMES",
    "_BLOCK_PRIVATE_NETWORKS",
    "_PRIVATE_NETWORK_PATTERNS",
    "_PROMPT_INJECTION_PATTERNS",
    "annotations",
    "os",
    "re",
    "urlparse",
]
