# ruff: noqa: F403, F405, E501
"""Verify one-shot CLI invocations exit non-zero on failure.

Reviewer feedback at HKUDS/CLI-Anything PR #251 flagged that handlers were
catching exceptions, printing via ``_output_error()``, then returning normally.
That made scripts and agents see failures as success. These tests pin the
contract: any failed command in one-shot mode must exit with code 1, while
the success path stays exit 0 and the REPL absorbs the exit so the loop
continues.

The subprocess tests use ``python -m cli_anything.sbox`` rather than the
installed ``cli-anything-sbox`` binary so the suite is portable across
environments where the launcher script may behave differently (e.g. Windows
+ Python 3.14 native launcher quirks).
"""

import json
import os
import subprocess
import sys
import pytest

CLI = [sys.executable, "-m", "cli_anything.sbox"]


def _run(args, cwd=None, env=None, timeout=30):
    """Run the CLI as a subprocess and return CompletedProcess (no check).

    ``stdin=DEVNULL`` is required on Windows + Python 3.14 + pytest where the
    parent test runner's stdin handle is not inheritable, otherwise Popen
    raises ``OSError: [WinError 6] The handle is invalid`` before the child
    even starts.
    """
    return subprocess.run(
        CLI + list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
    )


__all__ = [
    "CLI",
    "_run",
    "json",
    "os",
    "pytest",
    "subprocess",
    "sys",
]
