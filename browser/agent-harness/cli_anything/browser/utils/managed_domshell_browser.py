"""Managed agent-browser and local DOMShell server startup helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from cli_anything.browser.utils import domshell_runtime, secure_egress_runtime
from cli_anything.browser.utils.managed_domshell_contract import (
    AGENT_BROWSER_NAMESPACE,
    AGENT_BROWSER_SESSION,
    ManagedDOMShellError,
)
from cli_anything.browser.utils.managed_domshell_state import _port_ready, profile_dir


def _agent_browser(proxy_host: str, proxy_port: int, extension: Path, control_port: int, arguments: list[str]) -> dict[str, object]:
    executable = shutil.which("agent-browser")
    if not executable:
        raise ManagedDOMShellError("agent-browser is required for managed secure Chrome")
    command = [
        executable,
        "--session", AGENT_BROWSER_SESSION,
        "--namespace", AGENT_BROWSER_NAMESPACE,
        "--profile", str(profile_dir()),
        "--extension", str(extension),
        "--args", "--headless=new,--remote-allow-origins=http://localhost,--disable-quic,--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
        "--proxy", f"http://{proxy_host}:{proxy_port}",
        "--proxy-bypass", f"<-loopback>,127.0.0.1:{control_port}",
        "--json",
        *arguments,
    ]
    environment = os.environ.copy()
    for key in list(environment):
        if key.startswith("AGENT_BROWSER_") or key in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}:
            environment.pop(key, None)
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30, env=environment)
    except subprocess.TimeoutExpired as error:
        raise ManagedDOMShellError("Managed Chrome did not respond before the secure startup deadline") from error
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ManagedDOMShellError("Managed Chrome returned an invalid response") from error
    if completed.returncode or not payload.get("success"):
        raise ManagedDOMShellError("Managed Chrome could not be started with secure egress")
    data = payload.get("data")
    return data if isinstance(data, dict) else {}


def _start_mcp_server(token: str, mcp_port: int, ws_port: int) -> subprocess.Popen[bytes]:
    environment = {"PATH": os.environ.get("PATH", ""), "HOME": str(Path.home())}
    environment.update({
        "DOMSHELL_TOKEN": token,
        "DOMSHELL_MCP_PORT": str(mcp_port),
        "DOMSHELL_WS_PORT": str(ws_port),
        "DOMSHELL_MCP_HOST": "127.0.0.1",
        "npm_config_ignore_scripts": "true",
    })
    return subprocess.Popen(
        [*domshell_runtime.command("domshell"), "--granular", "--allow-write"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=secure_egress_runtime.runtime_dir(),
        start_new_session=True,
        env=environment,
    )


def _wait_for_port(port: int) -> None:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if _port_ready(port):
            return
        time.sleep(0.1)
    raise ManagedDOMShellError("Managed DOMShell MCP server did not become ready")


def _cdp_url(proxy_host: str, proxy_port: int, extension: Path, ws_port: int) -> str:
    data = _agent_browser(proxy_host, proxy_port, extension, ws_port, ["get", "cdp-url"])
    url = data.get("cdpUrl")
    if not isinstance(url, str) or not url.startswith("ws://127.0.0.1:"):
        raise ManagedDOMShellError("Managed Chrome did not expose a loopback CDP endpoint")
    return url
