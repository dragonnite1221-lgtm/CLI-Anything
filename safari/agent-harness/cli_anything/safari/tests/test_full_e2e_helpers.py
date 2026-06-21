# ruff: noqa: F403, F405, E501
"""E2E tests for cli-anything-safari — Requires Safari + macOS.

These tests interact with real Safari via the safari-mcp MCP server. They are
SKIPPED by default because:
1. Safari MCP kills stale instances (>10s) which can disrupt other agents
   using Safari MCP concurrently
2. E2E tests mutate browser state (open tabs, navigate, read cookies)
3. They require macOS + Safari with Apple Events enabled

To enable:
    export SAFARI_E2E=1
    python -m pytest cli_anything/safari/tests/test_full_e2e.py -v -s

To also enforce the installed command (not module fallback):
    CLI_ANYTHING_FORCE_INSTALLED=1 SAFARI_E2E=1 \\
        python -m pytest cli_anything/safari/tests/test_full_e2e.py -v -s
"""

import json
import os
import shutil
import subprocess
import sys
import pytest
from click.testing import CliRunner
from cli_anything.safari.utils.safari_backend import is_available
from cli_anything.safari.safari_cli import cli

SAFARI_E2E_ENABLED = os.environ.get("SAFARI_E2E", "").lower() in {"1", "true", "yes"}


def _should_skip_e2e() -> bool:
    """Decide whether to skip the E2E file.

    Evaluated lazily so that pytest --collect-only does not call
    ``is_available()`` (which would hit the npm registry with up to a
    15-second timeout) when the feature flag is off. Only when
    SAFARI_E2E=1 do we actually probe for safari-mcp availability.
    """
    if not SAFARI_E2E_ENABLED:
        return True
    return not is_available()[0]


pytestmark = pytest.mark.skipif(
    _should_skip_e2e(),
    reason=(
        "Safari E2E tests are disabled or safari-mcp is not available. "
        "Set SAFARI_E2E=1 and ensure Safari is installed with 'Allow "
        "JavaScript from Apple Events' enabled (Safari → Develop menu)."
    ),
)
TEST_URL = "https://example.com"


def _resolve_cli(name: str):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    This matches the pattern from HARNESS.md Phase 5.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    # Fallback: run as module
    module = "cli_anything.safari.safari_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


@pytest.fixture
def runner():
    return CliRunner()


__all__ = [
    "CliRunner",
    "SAFARI_E2E_ENABLED",
    "TEST_URL",
    "_resolve_cli",
    "_should_skip_e2e",
    "cli",
    "is_available",
    "json",
    "os",
    "pytest",
    "pytestmark",
    "runner",
    "shutil",
    "subprocess",
    "sys",
]
