# ruff: noqa: F403, F405, E501
"""E2E and subprocess tests for cli-anything-adguardhome.

Subprocess tests work without AdGuardHome (test CLI mechanics).
Docker tests require: docker pull adguard/adguardhome
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import pytest
import requests


def _resolve_cli(name: str) -> list[str]:
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(
            f"{name} not found in PATH. Install with:\n"
            f"  cd agent-harness && pip install -e ."
        )
    module = "cli_anything.adguardhome.adguardhome_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


AGH_TEST_PORT = 3001
AGH_TEST_HOST = "localhost"
AGH_CONTAINER = "agh-cli-test"


def _wait_for_adguardhome(port: int, timeout: int = 30) -> bool:
    """Wait until AdGuardHome API responds."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"http://localhost:{port}/control/status", timeout=2)
            if r.status_code in (200, 401, 403):
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False


def _configure_adguardhome(port: int, username: str, password: str) -> bool:
    """Run the setup wizard via the install API."""
    url = f"http://localhost:{port}/control/install/configure"
    payload = {
        "web": {"ip": "0.0.0.0", "port": 3000, "status": "", "can_autofix": False},
        "dns": {"ip": "0.0.0.0", "port": 53, "status": "", "can_autofix": False},
        "username": username,
        "password": password,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def agh_docker():
    """Start AdGuardHome in Docker for E2E tests, configure via install API."""
    username = "admin"
    password = "admin123"

    # Stop any existing container
    subprocess.run(["docker", "rm", "-f", AGH_CONTAINER], capture_output=True)

    # Start AdGuardHome container (no config mount - will use install API)
    result = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            AGH_CONTAINER,
            "-p",
            f"{AGH_TEST_PORT}:3000",
            "--cap-add=NET_ADMIN",
            "adguard/adguardhome",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.skip(f"Could not start AdGuardHome Docker: {result.stderr}")

    # Wait for setup wizard to be available
    deadline = time.time() + 30
    setup_ready = False
    while time.time() < deadline:
        try:
            r = requests.get(
                f"http://localhost:{AGH_TEST_PORT}/control/install/get_addresses",
                timeout=2,
            )
            if r.status_code == 200:
                setup_ready = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    if not setup_ready:
        subprocess.run(["docker", "rm", "-f", AGH_CONTAINER], capture_output=True)
        pytest.skip("AdGuardHome setup wizard not reachable in time")

    # Run setup wizard
    if not _configure_adguardhome(AGH_TEST_PORT, username, password):
        subprocess.run(["docker", "rm", "-f", AGH_CONTAINER], capture_output=True)
        pytest.skip("Could not configure AdGuardHome via install API")

    # Wait for configured instance to be ready
    if not _wait_for_adguardhome(AGH_TEST_PORT, timeout=20):
        subprocess.run(["docker", "rm", "-f", AGH_CONTAINER], capture_output=True)
        pytest.skip("AdGuardHome not ready after configuration")

    print(f"\n  AdGuardHome running at localhost:{AGH_TEST_PORT} (admin/admin123)")

    yield {
        "host": AGH_TEST_HOST,
        "port": AGH_TEST_PORT,
        "username": username,
        "password": password,
    }

    subprocess.run(["docker", "rm", "-f", AGH_CONTAINER], capture_output=True)


__all__ = [
    "AGH_CONTAINER",
    "AGH_TEST_HOST",
    "AGH_TEST_PORT",
    "Path",
    "_configure_adguardhome",
    "_resolve_cli",
    "_wait_for_adguardhome",
    "agh_docker",
    "json",
    "os",
    "pytest",
    "requests",
    "shutil",
    "subprocess",
    "sys",
    "time",
]
