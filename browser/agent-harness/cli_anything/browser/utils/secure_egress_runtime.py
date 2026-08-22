"""Lifecycle management for the private DNS-pinning proxy process."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

from cli_anything.browser.utils.process_identity import process_identity as _process_identity

try:
    import fcntl
except ImportError:  # pragma: no cover - this Unix process-group runtime fails closed elsewhere.
    fcntl = None


RUNTIME_ENV = "CLI_ANYTHING_BROWSER_RUNTIME_DIR"


class SecureEgressRuntimeError(RuntimeError):
    """The secure browser runtime cannot prove its proxy is available."""


def runtime_dir() -> Path:
    configured = os.environ.get(RUNTIME_ENV)
    base = Path(configured) if configured else Path.home() / ".cache" / "cli-anything-browser"
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    base.chmod(0o700)
    return base


def _state_path() -> Path:
    return runtime_dir() / "secure-egress-proxy.json"


@contextmanager
def _startup_lock():
    """Serialize state discovery, daemon startup, and state publication across clients."""

    if fcntl is None:
        raise SecureEgressRuntimeError("secure proxy startup requires an advisory file lock")
    lock_path = runtime_dir() / "secure-egress-proxy.lock"
    with lock_path.open("a", encoding="utf-8") as lock_file:
        lock_path.chmod(0o600)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _load_state() -> dict[str, object] | None:
    try:
        state_path = _state_path()
        if state_path.stat().st_mode & 0o077:
            return None
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            return None
        if not isinstance(state.get("host"), str) or not isinstance(state.get("port"), int):
            return None
        if not isinstance(state.get("pid"), int) or not isinstance(state.get("identity"), str):
            return None
        return state
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
        return None


def _alive(state: dict[str, object]) -> bool:
    try:
        pid = int(state["pid"])
        if _process_identity(pid) != state["identity"]:
            return False
        os.kill(pid, 0)
        with socket.create_connection((str(state["host"]), int(state["port"])), timeout=0.2):
            return True
    except (OSError, ValueError, TypeError):
        return False


def running_proxy() -> tuple[str, int] | None:
    """Return the existing live proxy endpoint without starting a new process."""

    state = _load_state()
    if state and _alive(state):
        return str(state["host"]), int(state["port"])
    return None


def ensure_proxy() -> tuple[str, int]:
    """Return a running loopback proxy, starting a private daemon if needed."""

    with _startup_lock():
        existing = running_proxy()
        if existing:
            return existing

        state_path = _state_path()
        try:
            state_path.unlink()
        except FileNotFoundError:
            pass
        log_path = runtime_dir() / "secure-egress-proxy.log"
        with log_path.open("ab", buffering=0) as log_file:
            log_path.chmod(0o600)
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "cli_anything.browser.utils.secure_egress_proxy",
                    "--state-file",
                    str(state_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            state = _load_state()
            if state and _alive(state):
                return str(state["host"]), int(state["port"])
            time.sleep(0.05)
        raise SecureEgressRuntimeError("Secure egress proxy did not become ready")


def stop_proxy() -> None:
    """Stop the proxy process recorded in the private runtime state, if present."""

    with _startup_lock():
        state = _load_state()
        if state:
            pid = int(state["pid"])
            if _process_identity(pid) == state["identity"]:
                try:
                    os.kill(pid, 15)
                except (OSError, ValueError, TypeError):
                    pass
                else:
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        try:
                            os.kill(pid, 0)
                        except OSError:
                            break
                        time.sleep(0.05)
                    else:
                        try:
                            os.kill(pid, 9)
                        except OSError:
                            pass
        try:
            _state_path().unlink()
        except FileNotFoundError:
            pass
