"""Managed Chrome/DOMShell lifecycle for the DNS-pinned browser runtime."""

from __future__ import annotations

from pathlib import Path
import secrets
import subprocess

from cli_anything.browser.utils.isolated_domshell_runtime import lifecycle_lock, start_isolated_runtime
from cli_anything.browser.utils.managed_domshell_contract import (
    DOMSHELL_EXTENSION_ENV,
    ManagedDOMShellError,
)
from cli_anything.browser.utils.managed_domshell_state import (
    _extension_dir,
    _free_loopback_port,
    _port_ready,
    _process_identity,
    _private_json,
    _state_path,
    _terminate_process_group,
    _write_private_json,
    existing_connection,
)


__all__ = [
    "DOMSHELL_EXTENSION_ENV",
    "ManagedDOMShellError",
    "ensure_managed_domshell",
    "managed_status",
    "stop_managed_domshell",
]


def _existing_connection(extension: Path) -> tuple[int, str] | None:
    """Return a still-live managed session while retaining facade injection hooks."""

    return existing_connection(extension, _state_path, _port_ready, _process_identity)


def ensure_managed_domshell() -> tuple[int, str]:
    """Return a private MCP port/token after enforcing managed secure egress."""

    with lifecycle_lock():
        return _ensure_managed_domshell()


def _ensure_managed_domshell() -> tuple[int, str]:
    extension = _extension_dir()
    existing = _existing_connection(extension)
    if existing:
        return existing
    _stop_managed_domshell()
    token, mcp_port, ws_port = secrets.token_urlsafe(32), _free_loopback_port(), _free_loopback_port()
    while ws_port == mcp_port:
        ws_port = _free_loopback_port()
    process = start_isolated_runtime(extension, token, mcp_port, ws_port)
    try:
        mcp_identity = _process_identity(process.pid)
        if mcp_identity is None:
            raise ManagedDOMShellError("unable to verify managed MCP process identity")
        _write_private_json(
            _state_path(),
            {
                "extension": str(extension),
                "mcp_port": mcp_port,
                "token": token,
                "mcp_pid": process.pid,
                "mcp_identity": mcp_identity,
            },
        )
        return mcp_port, token
    except Exception:
        _cleanup_failed_start(process)
        raise


def _cleanup_failed_start(process) -> None:
    _terminate_process_group(process.pid)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def stop_managed_domshell() -> None:
    """Stop the recorded MCP process and paired private egress proxy."""

    with lifecycle_lock():
        _stop_managed_domshell()


def _stop_managed_domshell() -> None:
    state = _private_json(_state_path())
    if state and isinstance(state.get("mcp_pid"), int) and isinstance(state.get("mcp_identity"), str):
        if _process_identity(state["mcp_pid"]) == state["mcp_identity"]:
            _terminate_process_group(state["mcp_pid"])
    try:
        _state_path().unlink()
    except FileNotFoundError:
        pass


def managed_status() -> dict[str, object]:
    """Return non-secret managed runtime state for CLI controls."""

    state = _private_json(_state_path())
    if not state:
        return {"managed": False, "reason": "not started"}
    port = state.get("mcp_port")
    return {"managed": isinstance(port, int) and _port_ready(port), "extension": state.get("extension"), "mcp_port": port}
