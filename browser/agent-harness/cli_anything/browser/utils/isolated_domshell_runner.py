"""Run the managed browser, DOMShell, and egress proxy inside one user network namespace."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from cli_anything.browser.utils import secure_egress_runtime
from cli_anything.browser.utils.managed_domshell_browser import _agent_browser, _start_mcp_server, _wait_for_ports
from cli_anything.browser.utils.managed_domshell_contract import DOMSHELL_EXTENSION_ENV, ManagedDOMShellError
from cli_anything.browser.utils.managed_domshell_extension import _configure_extension, _extension_id, _extension_options_target
from cli_anything.browser.utils.managed_domshell_state import _extension_dir
from cli_anything.browser.utils.process_identity import process_identity


def _private_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or path.stat().st_mode & 0o077:
        raise RuntimeError("isolated DOMShell configuration is invalid")
    return value


def _write_ready(path: Path) -> None:
    identity = process_identity(os.getpid())
    if identity is None:
        raise RuntimeError("isolated DOMShell runner cannot record its process identity")
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"ready": True, "identity": identity}), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def _configure_browser(extension: Path, token: str, mcp_port: int, ws_port: int) -> tuple[subprocess.Popen[bytes], str, int]:
    proxy_host, proxy_port = secure_egress_runtime.ensure_proxy()
    process = _start_mcp_server(token, mcp_port, ws_port)
    try:
        _wait_for_ports(process.pid, mcp_port, ws_port)
        _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])
        extension_id = _extension_id(extension)
        _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", f"chrome-extension://{extension_id}/options.html"])
        cdp_url = _agent_browser(proxy_host, proxy_port, extension, ws_port, ["get", "cdp-url"]).get("cdpUrl")
        if not isinstance(cdp_url, str) or not cdp_url.startswith("ws://127.0.0.1:"):
            raise ManagedDOMShellError("isolated managed Chrome did not expose a private CDP endpoint")
        _configure_extension(_extension_options_target(cdp_url, extension_id), token, ws_port)
        _agent_browser(proxy_host, proxy_port, extension, ws_port, ["open", "about:blank"])
        return process, proxy_host, proxy_port
    except Exception:
        _stop_process(process)
        secure_egress_runtime.stop_proxy()
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Start an isolated managed DOMShell runtime")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--ready-path", required=True, type=Path)
    arguments = parser.parse_args()
    config = _private_json(arguments.config)
    extension_path, token = config.get("extension"), config.get("token")
    mcp_port, ws_port = config.get("mcp_port"), config.get("ws_port")
    if not all((isinstance(extension_path, str), isinstance(token, str), isinstance(mcp_port, int), isinstance(ws_port, int))):
        raise RuntimeError("isolated DOMShell configuration is incomplete")
    os.environ[DOMSHELL_EXTENSION_ENV] = extension_path
    extension = _extension_dir()
    mcp_process, proxy_host, proxy_port = _configure_browser(extension, token, mcp_port, ws_port)
    arguments.config.unlink(missing_ok=True)
    _write_ready(arguments.ready_path)
    stopping = False

    def stop(*_args) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while not stopping:
            time.sleep(0.2)
    finally:
        try:
            _agent_browser(proxy_host, proxy_port, extension, ws_port, ["close", "--all"])
        except Exception:
            pass
        _stop_process(mcp_process)
        secure_egress_runtime.stop_proxy()
        arguments.ready_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
