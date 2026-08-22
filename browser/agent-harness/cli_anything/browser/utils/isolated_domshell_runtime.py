"""Host-side launcher for the user-network-namespaced managed DOMShell runtime."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from cli_anything.browser.utils.managed_domshell_contract import ManagedDOMShellError
from cli_anything.browser.utils.secure_egress_runtime import runtime_dir

try:
    import fcntl
except ImportError:  # pragma: no cover - secure managed Chrome is Linux-only.
    fcntl = None


@contextmanager
def lifecycle_lock():
    """Serialize state inspection, isolated runtime launch, and teardown across CLI processes."""

    if fcntl is None:
        raise ManagedDOMShellError("managed secure Chrome requires a Unix advisory lock")
    lock_path = runtime_dir() / "isolated-domshell.lock"
    with lock_path.open("a", encoding="utf-8") as lock_file:
        lock_path.chmod(0o600)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _write_private_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def _isolation_tools() -> tuple[str, str, str]:
    if not sys.platform.startswith("linux"):
        raise ManagedDOMShellError("managed secure Chrome is supported only on Linux because it requires a user network namespace")
    rootlesskit, slirp, newuidmap = shutil.which("rootlesskit"), shutil.which("slirp4netns"), shutil.which("newuidmap")
    if not rootlesskit or not slirp or not newuidmap:
        raise ManagedDOMShellError("managed secure Chrome requires rootlesskit, slirp4netns, and uidmap for CDP isolation")
    return rootlesskit, slirp, newuidmap


def _terminate(process: subprocess.Popen[bytes]) -> None:
    """Reap a launcher that failed before its state became visible to callers."""

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def start_isolated_runtime(extension: Path, token: str, mcp_port: int, ws_port: int) -> subprocess.Popen[bytes]:
    """Launch one private browser network namespace and wait for its authenticated MCP bridge."""

    rootlesskit, _slirp, _newuidmap = _isolation_tools()
    config_path, ready_path = runtime_dir() / "isolated-domshell-config.json", runtime_dir() / "isolated-domshell-ready.json"
    ready_path.unlink(missing_ok=True)
    _write_private_json(config_path, {"extension": str(extension), "token": token, "mcp_port": mcp_port, "ws_port": ws_port})
    log_path = runtime_dir() / "isolated-domshell.log"
    try:
        with log_path.open("ab", buffering=0) as log_file:
            log_path.chmod(0o600)
            process = subprocess.Popen(
                [
                    rootlesskit,
                    "--net=slirp4netns",
                    "--copy-up=/etc",
                    "--disable-host-loopback",
                    "--port-driver=builtin",
                    "--publish",
                    f"127.0.0.1:{mcp_port}:{mcp_port}/tcp",
                    sys.executable,
                    "-m",
                    "cli_anything.browser.utils.isolated_domshell_runner",
                    "--config",
                    str(config_path),
                    "--ready-path",
                    str(ready_path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except OSError as exc:
        config_path.unlink(missing_ok=True)
        raise ManagedDOMShellError("could not launch isolated managed Chrome") from exc
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if ready_path.exists():
            return process
        if process.poll() is not None:
            config_path.unlink(missing_ok=True)
            raise ManagedDOMShellError("isolated managed Chrome exited before it became ready")
        time.sleep(0.1)
    _terminate(process)
    config_path.unlink(missing_ok=True)
    raise ManagedDOMShellError("isolated managed Chrome did not become ready")
