# ruff: noqa: F403, F405, E501
"""Unit tests for the PM2 CLI-Anything harness.

All subprocess calls are mocked -- no pm2 binary required.
Covers: pm2_backend, core/processes, core/lifecycle, core/logs, core/system,
        pm2_cli output formatting, and error handling.
"""

import json
import subprocess
from unittest import mock
from unittest.mock import MagicMock, patch
import pytest


def _make_run_result(stdout="", stderr="", returncode=0):
    """Build a mock subprocess.CompletedProcess."""
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.stdout = stdout
    r.stderr = stderr
    r.returncode = returncode
    return r


FAKE_JLIST = json.dumps(
    [
        {
            "pm_id": 0,
            "name": "seaclip-dev",
            "pid": 12345,
            "monit": {"cpu": 2.5, "memory": 52428800},
            "pm2_env": {
                "status": "online",
                "restart_time": 3,
                "pm_uptime": 1700000000000,
                "pm_exec_path": "/app/index.js",
                "pm_cwd": "/app",
                "exec_interpreter": "node",
                "exec_mode": "fork_mode",
                "node_version": "20.11.0",
            },
        },
        {
            "pm_id": 1,
            "name": "hub-dashboard",
            "pid": 12346,
            "monit": {"cpu": 0.1, "memory": 10485760},
            "pm2_env": {
                "status": "stopped",
                "restart_time": 0,
                "pm_uptime": 0,
                "pm_exec_path": "/dash/server.js",
                "pm_cwd": "/dash",
                "exec_interpreter": "node",
                "exec_mode": "fork_mode",
                "node_version": "20.11.0",
            },
        },
    ]
)


__all__ = [
    "FAKE_JLIST",
    "MagicMock",
    "_make_run_result",
    "json",
    "mock",
    "patch",
    "pytest",
    "subprocess",
]
