"""Private state and local resource validation for managed DOMShell."""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import stat

from cli_anything.browser.utils import secure_egress_runtime
from cli_anything.browser.utils.managed_domshell_contract import DOMSHELL_EXTENSION_ENV, ManagedDOMShellError


def _process_identity(pid: int) -> str | None:
    """Return Linux's non-reusable process start identifier, when available."""

    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        closing = stat.rfind(")")
        fields = stat[closing + 2 :].split()
        return fields[19] if closing >= 0 and len(fields) > 19 else None
    except OSError:
        return None


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
        _validate_extension_tree(path)
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ManagedDOMShellError("DOMShell extension manifest is unreadable") from error
    if data.get("manifest_version") != 3 or data.get("name") != "DOMShell — Browser Filesystem for AI Agents":
        raise ManagedDOMShellError("DOMShell extension manifest does not identify the expected extension")
    return path


def _validate_extension_tree(path: Path) -> None:
    """Reject extension code that another local account can replace before Chrome loads it."""

    owner = os.getuid()
    _validate_extension_entry(path, owner, "directory")
    for entry in path.rglob("*"):
        _validate_extension_entry(entry, owner, "asset")
    for ancestor in path.parents:
        info = ancestor.stat()
        if info.st_uid not in {owner, 0}:
            raise ManagedDOMShellError("DOMShell extension ancestor must be owned by the current user or root")
        writable = info.st_mode & 0o022
        if writable and not (stat.S_ISDIR(info.st_mode) and info.st_mode & stat.S_ISVTX):
            raise ManagedDOMShellError("DOMShell extension ancestor must not be group- or world-writable")


def _validate_extension_entry(path: Path, owner: int, label: str) -> None:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        raise ManagedDOMShellError(f"DOMShell extension {label} must not be a symlink")
    if info.st_uid not in {owner, 0}:
        raise ManagedDOMShellError(f"DOMShell extension {label} must be owned by the current user or root")
    if info.st_mode & 0o022:
        raise ManagedDOMShellError(f"DOMShell extension {label} must not be group- or world-writable")


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


def existing_connection(extension: Path, state_path, port_ready, process_identity) -> tuple[int, str] | None:
    state = _private_json(state_path())
    if not state or state.get("extension") != str(extension):
        return None
    port, token, pid, identity = state.get("mcp_port"), state.get("token"), state.get("mcp_pid"), state.get("mcp_identity")
    proxy_host, proxy_port = state.get("proxy_host"), state.get("proxy_port")
    if not all((isinstance(port, int), isinstance(token, str), isinstance(pid, int), isinstance(identity, str), isinstance(proxy_host, str), isinstance(proxy_port, int), port_ready(port))):
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    if process_identity(pid) != identity:
        return None
    if secure_egress_runtime.running_proxy() != (proxy_host, proxy_port):
        return None
    return port, token
