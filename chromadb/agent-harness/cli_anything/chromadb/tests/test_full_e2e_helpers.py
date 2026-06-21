# ruff: noqa: F403, F405, E501
"""End-to-end tests for the ChromaDB CLI-Anything harness.

These tests call the REAL ChromaDB server at localhost:8000 via subprocess,
exercising the installed CLI binary. They validate exit codes, JSON output
parsing, and actual server responses.

Requirements:
- ChromaDB running at localhost:8000
- cli-anything-chromadb installed (pip install -e .)
"""

import json
import os
import shutil
import subprocess
import sys
import pytest


def _resolve_cli():
    """Find the cli-anything-chromadb binary.

    Checks in order:
    1. Installed console_script on PATH
    2. python -m cli_anything.chromadb fallback
    """
    # Check if the console script is on PATH
    cli_path = shutil.which("cli-anything-chromadb")
    if cli_path:
        return [cli_path]
    # Fallback: run as module
    return [sys.executable, "-m", "cli_anything.chromadb"]


CLI = _resolve_cli()


def _run(args, timeout=15):
    """Run the CLI with the given args and return CompletedProcess."""
    cmd = CLI + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _chromadb_available():
    """Check if ChromaDB is reachable at localhost:8000."""
    try:
        import requests

        r = requests.get("http://localhost:8000/api/v2/heartbeat", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _chromadb_available(), reason="ChromaDB server not available at localhost:8000"
)


__all__ = [
    "CLI",
    "_chromadb_available",
    "_resolve_cli",
    "_run",
    "json",
    "os",
    "pytest",
    "pytestmark",
    "shutil",
    "subprocess",
    "sys",
]
