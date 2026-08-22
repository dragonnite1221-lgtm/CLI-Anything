"""Start DOMShell only inside a Chrome instance protected by secure egress."""

from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

import websocket

from cli_anything.browser.utils import secure_egress_runtime
from cli_anything.browser.utils import domshell_runtime


DOMSHELL_EXTENSION_ENV = "CLI_ANYTHING_DOMSHELL_EXTENSION_DIR"
AGENT_BROWSER_SESSION = "cabsec"
AGENT_BROWSER_NAMESPACE = "cabsec"


class ManagedDOMShellError(RuntimeError):
    """A managed Chrome/DOMShell session cannot be safely established."""


def _terminate_process_group(pid: int) -> None:
    """Terminate a detached local DOMShell process group."""

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
        raise ManagedDOMShellError(
            f"{DOMSHELL_EXTENSION_ENV} must point to a locally built DOMShell extension"
        )
    path = Path(configured).expanduser().resolve()
    manifest = path / "manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ManagedDOMShellError("DOMShell extension manifest is unreadable") from error
    if data.get("manifest_version") != 3 or data.get("name") != "DOMShell — Browser Filesystem for AI Agents":
        raise ManagedDOMShellError("DOMShell extension manifest does not identify the expected extension")
    if path.stat().st_mode & 0o022:
        raise ManagedDOMShellError("DOMShell extension directory must not be group- or world-writable")
    if manifest.stat().st_mode & 0o022:
        raise ManagedDOMShellError("DOMShell extension must not be group- or world-writable")
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


def _profile_dir() -> Path:
    profile = secure_egress_runtime.runtime_dir() / "chrome-profile"
    profile.mkdir(mode=0o700, exist_ok=True)
    profile.chmod(0o700)
    return profile


def _agent_browser(
    proxy_host: str,
    proxy_port: int,
    extension: Path,
    control_port: int,
    arguments: list[str],
) -> dict[str, object]:
    executable = shutil.which("agent-browser")
    if not executable:
        raise ManagedDOMShellError("agent-browser is required for managed secure Chrome")
    profile = _profile_dir()
    command = [
        executable,
        "--session", AGENT_BROWSER_SESSION,
        "--namespace", AGENT_BROWSER_NAMESPACE,
        "--profile", str(profile),
        "--extension", str(extension),
        # agent-browser switches to headed mode when an extension is present.
        # Explicit headless Chromium keeps the managed CLI usable on servers
        # with no X display while retaining the extension service worker.
        # Limit CDP WebSocket origins to this local supervisor, rather than
        # opening Chrome's debugging endpoint to arbitrary web origins.
        "--args", (
            "--headless=new,--remote-allow-origins=http://localhost,"
            "--disable-quic,--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
        ),
        "--proxy", f"http://{proxy_host}:{proxy_port}",
        # The extension's authenticated local WebSocket gets the one explicit
        # bypass.  All other loopback/private page navigation still reaches the
        # proxy and is rejected.  The port is random per managed session and
        # DOMShell also requires the independent connection token.
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
    environment.update(
        {
            "DOMSHELL_TOKEN": token,
            "DOMSHELL_MCP_PORT": str(mcp_port),
            "DOMSHELL_WS_PORT": str(ws_port),
            "DOMSHELL_MCP_HOST": "127.0.0.1",
            "npm_config_ignore_scripts": "true",
        }
    )
    return subprocess.Popen(
        # The browser harness calls DOMShell's granular MCP tools
        # (domshell_open, domshell_ls, ...), not the single shell tool.
        [
            *domshell_runtime.command("domshell"),
            "--granular",
            # Navigation and the CLI's existing click/type actions are
            # DOMShell write-tier operations. The MCP port/token stay
            # private to this process; sensitive-cookie access remains off.
            "--allow-write",
        ],
        stdin=subprocess.DEVNULL,
        # DOMShell prints its runtime token during startup. Keep it out of a
        # durable log; runtime state has a 0600 owner-only token file instead.
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=secure_egress_runtime.runtime_dir(),
        start_new_session=True,
        env=environment,
    )


def _wait_for_port(port: int) -> None:
    # The server is already installed through the lockfile-verified setup
    # command, so startup is deterministic and never downloads a package.
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


def _extension_id(extension: Path) -> str:
    """Read the Chrome-assigned ID for the exact loaded local extension path."""

    preferences = _profile_dir() / "Default" / "Preferences"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            data = json.loads(preferences.read_text(encoding="utf-8"))
            settings = data["extensions"]["settings"]
            for identifier, setting in settings.items():
                if not isinstance(identifier, str) or not isinstance(setting, dict):
                    continue
                stored_path = setting.get("path")
                if isinstance(stored_path, str) and Path(stored_path).resolve() == extension:
                    return identifier
        except (FileNotFoundError, OSError, ValueError, KeyError, TypeError):
            pass
        time.sleep(0.1)
    raise ManagedDOMShellError("Managed Chrome did not register the DOMShell extension")


def _extension_options_target(cdp_url: str, extension_id: str) -> str:
    """Return the debugger URL of DOMShell's controlled options page.

    MV3 workers can be asleep until an extension event occurs. The options page
    is a reliable extension-context target; writing chrome.storage there wakes
    the service worker through its storage-change listener.
    """

    parsed = urlsplit(cdp_url)
    endpoint = f"http://{parsed.netloc}/json/list"
    options_url = f"chrome-extension://{extension_id}/options.html"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            with urlopen(endpoint, timeout=1) as response:
                targets = json.load(response)
            for target in targets:
                if target.get("type") == "page" and target.get("url") == options_url:
                    return str(target["webSocketDebuggerUrl"])
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(0.1)
    raise ManagedDOMShellError("Managed Chrome did not expose the DOMShell options page")


def _configure_extension(worker_url: str, token: str, ws_port: int) -> None:
    expression = f"chrome.storage.local.set({json.dumps({'ws_enabled': True, 'ws_token': token, 'ws_port': ws_port})})"
    connection: websocket.WebSocket | None = None
    try:
        connection = websocket.create_connection(worker_url, timeout=5, origin="http://localhost")
        connection.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": expression, "awaitPromise": True}}))
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                response = json.loads(connection.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if response.get("id") == 1:
                if "error" in response or response.get("result", {}).get("exceptionDetails"):
                    raise ManagedDOMShellError("Managed DOMShell extension rejected secure connection settings")
                return
        raise ManagedDOMShellError("Managed DOMShell extension did not acknowledge secure connection settings")
    except (OSError, ValueError, websocket.WebSocketException) as error:
        if isinstance(error, ManagedDOMShellError):
            raise
        raise ManagedDOMShellError("Could not configure the managed DOMShell extension") from error
    finally:
        if connection is not None:
            connection.close()


def _existing_connection(extension: Path) -> tuple[int, str] | None:
    state = _private_json(_state_path())
    if not state or state.get("extension") != str(extension):
        return None
    port, token, pid = state.get("mcp_port"), state.get("token"), state.get("mcp_pid")
    proxy_host, proxy_port = state.get("proxy_host"), state.get("proxy_port")
    if (
        not isinstance(port, int)
        or not isinstance(token, str)
        or not isinstance(pid, int)
        or not isinstance(proxy_host, str)
        or not isinstance(proxy_port, int)
        or not _port_ready(port)
    ):
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    if secure_egress_runtime.running_proxy() != (proxy_host, proxy_port):
        return None
    return port, token


def ensure_managed_domshell() -> tuple[int, str]:
    """Return the private MCP port/token after enforcing the managed egress path."""

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
        _wait_for_port(mcp_port)
        _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])
        extension_id = _extension_id(extension)
        _agent_browser(
            proxy_host,
            proxy_port,
            extension,
            ws_port,
            ["open", f"chrome-extension://{extension_id}/options.html"],
        )
        _configure_extension(
            _extension_options_target(
                _cdp_url(proxy_host, proxy_port, extension, ws_port), extension_id
            ),
            token,
            ws_port,
        )
        _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])
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
        raise


def _stop_agent_browser() -> None:
    executable = shutil.which("agent-browser")
    if executable:
        try:
            subprocess.run(
                [
                    executable,
                    "--session", AGENT_BROWSER_SESSION,
                    "--namespace", AGENT_BROWSER_NAMESPACE,
                    "close",
                    "--all",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        except subprocess.TimeoutExpired:
            pass


def stop_managed_domshell() -> None:
    """Stop the recorded MCP process and the paired private egress proxy."""

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
    """Return non-secret runtime state for the CLI's secure-runtime controls."""

    state = _private_json(_state_path())
    if not state:
        return {"managed": False, "reason": "not started"}
    port = state.get("mcp_port")
    return {
        "managed": isinstance(port, int) and _port_ready(port),
        "extension": state.get("extension"),
        "mcp_port": port,
    }
