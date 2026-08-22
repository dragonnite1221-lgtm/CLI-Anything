"""Configure the verified DOMShell extension inside managed Chrome."""

from __future__ import annotations

import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

import websocket

from cli_anything.browser.utils.managed_domshell_contract import ManagedDOMShellError
from cli_anything.browser.utils.managed_domshell_state import profile_dir


def _extension_id(extension: Path) -> str:
    preferences = profile_dir() / "Default" / "Preferences"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            settings = json.loads(preferences.read_text(encoding="utf-8"))["extensions"]["settings"]
            for identifier, setting in settings.items():
                stored_path = setting.get("path") if isinstance(setting, dict) else None
                if isinstance(identifier, str) and isinstance(stored_path, str) and Path(stored_path).resolve() == extension:
                    return identifier
        except (FileNotFoundError, OSError, ValueError, KeyError, TypeError):
            pass
        time.sleep(0.1)
    raise ManagedDOMShellError("Managed Chrome did not register the DOMShell extension")


def _extension_options_target(cdp_url: str, extension_id: str) -> str:
    endpoint = f"http://{urlsplit(cdp_url).netloc}/json/list"
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
