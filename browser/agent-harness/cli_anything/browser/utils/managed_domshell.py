"""Managed Chrome/DOMShell lifecycle for the DNS-pinned browser runtime."""

from __future__ import annotations

import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess

from cli_anything.browser.utils import domshell_runtime
from cli_anything.browser.utils import secure_egress_runtime
from cli_anything.browser.utils.managed_domshell_browser import (
    _agent_browser,
    _cdp_url,
    _start_mcp_server,
    _wait_for_port,
)
from cli_anything.browser.utils.managed_domshell_contract import (
    AGENT_BROWSER_NAMESPACE,
    AGENT_BROWSER_SESSION,
    DOMSHELL_EXTENSION_ENV,
    ManagedDOMShellError,
)
from cli_anything.browser.utils.managed_domshell_extension import (
    _configure_extension,
    _extension_id,
    _extension_options_target,
)
from cli_anything.browser.utils.managed_domshell_state import (
    _extension_dir,
    _free_loopback_port,
    _port_ready,
    _private_json,
    _state_path,
    _terminate_process_group,
    _write_private_json,
    existing_connection,
)


__all__ = [
    "DOMSHELL_EXTENSION_ENV",
    "ManagedDOMShellError",
    "domshell_runtime",
    "ensure_managed_domshell",
    "managed_status",
    "stop_managed_domshell",
]


def _existing_connection(extension: Path) -> tuple[int, str] | None:
    """Return a still-live managed session while retaining facade injection hooks."""

    return existing_connection(extension, _state_path, _port_ready)


def ensure_managed_domshell() -> tuple[int, str]:
    """Return a private MCP port/token after enforcing managed secure egress."""

    extension = _extension_dir()
    existing = _existing_connection(extension)
    if existing:
        return existing
    proxy_host, proxy_port = secure_egress_runtime.ensure_proxy()
    token, mcp_port, ws_port = secrets.token_urlsafe(32), _free_loopback_port(), _free_loopback_port()
    while ws_port == mcp_port:
        ws_port = _free_loopback_port()
    process = _start_mcp_server(token, mcp_port, ws_port)
    try:
        _configure_managed_extension(proxy_host, proxy_port, extension, token, ws_port, mcp_port)
        _write_private_json(
            _state_path(),
            {
                "extension": str(extension),
                "mcp_port": mcp_port,
                "token": token,
                "mcp_pid": process.pid,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
            },
        )
        return mcp_port, token
    except Exception:
        _cleanup_failed_start(process)
        raise


def _configure_managed_extension(proxy_host, proxy_port, extension, token, ws_port, mcp_port) -> None:
    _wait_for_port(mcp_port)
    _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])
    extension_id = _extension_id(extension)
    _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", f"chrome-extension://{extension_id}/options.html"])
    _configure_extension(
        _extension_options_target(_cdp_url(proxy_host, proxy_port, extension, ws_port), extension_id),
        token,
        ws_port,
    )
    _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])


def _cleanup_failed_start(process) -> None:
    _terminate_process_group(process.pid)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            process.kill()
    _stop_agent_browser()
    secure_egress_runtime.stop_proxy()


def _stop_agent_browser() -> None:
    executable = shutil.which("agent-browser")
    if not executable:
        return
    try:
        subprocess.run(
            [executable, "--session", AGENT_BROWSER_SESSION, "--namespace", AGENT_BROWSER_NAMESPACE, "close", "--all"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass


def stop_managed_domshell() -> None:
    """Stop the recorded MCP process and paired private egress proxy."""

    state = _private_json(_state_path())
    if state and isinstance(state.get("mcp_pid"), int):
        _terminate_process_group(state["mcp_pid"])
    try:
        _state_path().unlink()
    except FileNotFoundError:
        pass
    _stop_agent_browser()
    secure_egress_runtime.stop_proxy()


def managed_status() -> dict[str, object]:
    """Return non-secret managed runtime state for CLI controls."""

    state = _private_json(_state_path())
    if not state:
        return {"managed": False, "reason": "not started"}
    port = state.get("mcp_port")
    return {"managed": isinstance(port, int) and _port_ready(port), "extension": state.get("extension"), "mcp_port": port}
