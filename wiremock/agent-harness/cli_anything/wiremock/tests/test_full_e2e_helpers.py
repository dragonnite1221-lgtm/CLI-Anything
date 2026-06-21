# ruff: noqa: F403, F405, E501
"""E2E / subprocess tests for the cli-anything-wiremock CLI.

Tests that require a live WireMock server are automatically skipped unless
the WIREMOCK_URL environment variable is set (e.g. WIREMOCK_URL=http://localhost:8080).

Tests for --help and argument parsing work without a server.
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

CLI_ENV_KEY = "CLI_ANYTHING_FORCE_INSTALLED"


def _resolve_cli(name: str) -> list:
    """Resolve CLI name to a command list, supporting installed and dev modes.

    Returns a list suitable for use as the first argument to subprocess.run().
    """
    if os.environ.get(CLI_ENV_KEY):
        return [name]
    found = shutil.which(name)
    if found:
        return [found]
    # Fall back to running the module directly
    return [sys.executable, "-m", "cli_anything.wiremock.wiremock_cli"]


CLI_CMD = _resolve_cli("cli-anything-wiremock")
WIREMOCK_URL = os.environ.get("WIREMOCK_URL", "")
LIVE_SERVER_AVAILABLE = bool(WIREMOCK_URL)
skip_no_server = unittest.skipUnless(
    LIVE_SERVER_AVAILABLE,
    "WIREMOCK_URL not set — skipping live server tests",
)


def _run(
    *args, env_extras: dict = None, input_text: str = None
) -> subprocess.CompletedProcess:
    """Run the CLI with the given arguments and return the CompletedProcess."""
    env = os.environ.copy()
    if WIREMOCK_URL:
        from urllib.parse import urlparse

        parsed = urlparse(WIREMOCK_URL)
        env["WIREMOCK_HOST"] = parsed.hostname or "localhost"
        env["WIREMOCK_PORT"] = str(parsed.port or 8080)
        env["WIREMOCK_SCHEME"] = parsed.scheme or "http"
    if env_extras:
        env.update(env_extras)
    return subprocess.run(
        CLI_CMD + list(args),
        capture_output=True,
        text=True,
        env=env,
        input=input_text,
    )


__all__ = [
    "CLI_CMD",
    "CLI_ENV_KEY",
    "LIVE_SERVER_AVAILABLE",
    "WIREMOCK_URL",
    "_resolve_cli",
    "_run",
    "json",
    "os",
    "shutil",
    "skip_no_server",
    "subprocess",
    "sys",
    "unittest",
]
