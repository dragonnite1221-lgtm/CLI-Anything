"""Private state and local resource validation for managed DOMShell."""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket

from cli_anything.browser.utils import secure_egress_runtime
from cli_anything.browser.utils.managed_domshell_contract import DOMSHELL_EXTENSION_ENV, ManagedDOMShellError


def _terminate_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return


def _state_path() -> Path:
    return secure_egress_runtime.runtime_dir() / "managed-domshell.json"


def _private_json(path: Path) -> dict[str, object] | None:
    try:
        if path.stat().st_mode & 0o077:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
        return None


def _write_private_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def _extension_dir() -> Path:
    configured = os.environ.get(DOMSHELL_EXTENSION_ENV)
    if not configured:
        raise ManagedDOMShellError(f"{DOMSHELL_EXTENSION_ENV} must point to a locally built DOMShell extension")
    path = Path(configured).expanduser().resolve()
    manifest = path / "manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ManagedDOMShellError("DOMShell extension manifest is unreadable") from error
    if data.get("manifest_version") != 3 or data.get("name") != "DOMShell — Browser Filesystem for AI Agents":
        raise ManagedDOMShellError("DOMShell extension manifest does not identify the expected extension")
    if path.stat().st_mode & 0o022 or manifest.stat().st_mode & 0o022:
        raise ManagedDOMShellError("DOMShell extension directory must not be group- or world-writable")
    return path


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _port_ready(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def profile_dir() -> Path:
    profile = secure_egress_runtime.runtime_dir() / "chrome-profile"
    profile.mkdir(mode=0o700, exist_ok=True)
    profile.chmod(0o700)
    return profile


def existing_connection(extension: Path, state_path, port_ready) -> tuple[int, str] | None:
    state = _private_json(state_path())
    if not state or state.get("extension") != str(extension):
        return None
    port, token, pid = state.get("mcp_port"), state.get("token"), state.get("mcp_pid")
    proxy_host, proxy_port = state.get("proxy_host"), state.get("proxy_port")
    if not all((isinstance(port, int), isinstance(token, str), isinstance(pid, int), isinstance(proxy_host, str), isinstance(proxy_port, int), port_ready(port))):
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    if secure_egress_runtime.running_proxy() != (proxy_host, proxy_port):
        return None
    return port, token
