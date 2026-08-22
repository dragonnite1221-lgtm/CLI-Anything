"""Unit tests for the managed DOMShell secure-runtime contract."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from cli_anything.browser.utils import managed_domshell
from cli_anything.browser.utils import managed_domshell_extension


def test_extension_must_be_explicit(monkeypatch):
    monkeypatch.delenv(managed_domshell.DOMSHELL_EXTENSION_ENV, raising=False)

    with pytest.raises(managed_domshell.ManagedDOMShellError, match="must point"):
        managed_domshell._extension_dir()


def test_extension_manifest_must_identify_domshell(monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"manifest_version": 3, "name": "other"}), encoding="utf-8")
    manifest.chmod(0o600)
    monkeypatch.setenv(managed_domshell.DOMSHELL_EXTENSION_ENV, str(tmp_path))

    with pytest.raises(managed_domshell.ManagedDOMShellError, match="expected extension"):
        managed_domshell._extension_dir()


def test_extension_directory_must_not_be_group_writable(monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"manifest_version": 3, "name": "DOMShell — Browser Filesystem for AI Agents"}),
        encoding="utf-8",
    )
    manifest.chmod(0o600)
    tmp_path.chmod(0o770)
    monkeypatch.setenv(managed_domshell.DOMSHELL_EXTENSION_ENV, str(tmp_path))

    with pytest.raises(managed_domshell.ManagedDOMShellError, match="directory"):
        managed_domshell._extension_dir()


def test_extension_assets_must_not_be_group_writable(monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"manifest_version": 3, "name": "DOMShell — Browser Filesystem for AI Agents"}),
        encoding="utf-8",
    )
    asset = tmp_path / "service-worker.js"
    asset.write_text("// unsafe", encoding="utf-8")
    asset.chmod(0o666)
    tmp_path.chmod(0o700)
    monkeypatch.setenv(managed_domshell.DOMSHELL_EXTENSION_ENV, str(tmp_path))

    with pytest.raises(managed_domshell.ManagedDOMShellError, match="asset"):
        managed_domshell._extension_dir()


def test_extension_control_request_bypasses_ambient_proxies(monkeypatch):
    captured: dict[str, object] = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps([{"type": "page", "url": "chrome-extension://expected/options.html", "webSocketDebuggerUrl": "ws://127.0.0.1:1234"}]).encode()

    class Opener:
        def open(self, endpoint, timeout):
            captured["endpoint"] = endpoint
            captured["timeout"] = timeout
            return Response()

    monkeypatch.setattr(managed_domshell_extension, "ProxyHandler", lambda proxies: captured.setdefault("proxies", proxies) or SimpleNamespace())
    monkeypatch.setattr(managed_domshell_extension, "build_opener", lambda handler: Opener())

    assert managed_domshell_extension._extension_options_target("ws://127.0.0.1:9222/devtools/browser", "expected") == "ws://127.0.0.1:1234"
    assert captured["proxies"] == {}


def test_existing_connection_requires_private_state_and_live_mcp(monkeypatch, tmp_path):
    extension = tmp_path / "extension"
    extension.mkdir()
    state_path = tmp_path / "managed-domshell.json"
    state_path.write_text(
        json.dumps(
            {
                "extension": str(extension),
                "mcp_port": 3456,
                "token": "secret",
                "mcp_pid": 123,
                "mcp_identity": "12345",
                "proxy_host": "127.0.0.1",
                "proxy_port": 4567,
            }
        ),
        encoding="utf-8",
    )
    state_path.chmod(0o600)
    monkeypatch.setattr(managed_domshell, "_state_path", lambda: state_path)
    monkeypatch.setattr(managed_domshell, "_port_ready", lambda port: port == 3456)
    monkeypatch.setattr(managed_domshell.os, "kill", lambda pid, signal: None)
    monkeypatch.setattr(managed_domshell, "_process_identity", lambda pid: "12345")
    monkeypatch.setattr(
        managed_domshell.secure_egress_runtime,
        "running_proxy",
        lambda: ("127.0.0.1", 4567),
    )

    assert managed_domshell._existing_connection(extension) == (3456, "secret")


def test_secure_stop_never_signals_a_reused_mcp_pid(monkeypatch, tmp_path):
    state_path = tmp_path / "managed-domshell.json"
    state_path.write_text(json.dumps({"mcp_pid": 123, "mcp_identity": "original"}), encoding="utf-8")
    state_path.chmod(0o600)
    terminated: list[int] = []
    monkeypatch.setattr(managed_domshell, "_state_path", lambda: state_path)
    monkeypatch.setattr(managed_domshell, "_process_identity", lambda pid: "replacement")
    monkeypatch.setattr(managed_domshell, "_terminate_process_group", terminated.append)
    monkeypatch.setattr(managed_domshell.secure_egress_runtime, "stop_proxy", lambda: None)

    managed_domshell.stop_managed_domshell()

    assert terminated == []
    assert not state_path.exists()


def test_managed_browser_bypasses_only_the_random_extension_control_port(monkeypatch, tmp_path):
    captured: dict[str, object] = {}
    executable = tmp_path / "agent-browser"
    executable.write_text("", encoding="utf-8")

    class Completed:
        returncode = 0
        stdout = '{"success": true, "data": {}}'

    def fake_run(command, **_kwargs):
        captured["command"] = command
        return Completed()

    monkeypatch.setattr(managed_domshell.shutil, "which", lambda _name: str(executable))
    monkeypatch.setattr(managed_domshell.subprocess, "run", fake_run)
    monkeypatch.setattr(managed_domshell.secure_egress_runtime, "runtime_dir", lambda: tmp_path)

    managed_domshell._agent_browser("127.0.0.1", 45123, tmp_path, 49876, ["open", "about:blank"])

    command = captured["command"]
    assert (
        "--headless=new,--remote-allow-origins=http://localhost,"
        "--disable-quic,--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
    ) in command
    assert "<-loopback>,127.0.0.1:49876" in command


def test_mcp_server_requests_granular_tools(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    class Process:
        pid = 123

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return Process()

    monkeypatch.setattr(managed_domshell.secure_egress_runtime, "runtime_dir", lambda: tmp_path)
    monkeypatch.setattr(managed_domshell.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        managed_domshell.domshell_runtime,
        "command",
        lambda binary: ["node", f"/verified/{binary}.js"],
    )

    managed_domshell._start_mcp_server("test-token", 3456, 4567)

    assert captured["command"][:2] == ["node", "/verified/domshell.js"]
    assert captured["command"][-2:] == ["--granular", "--allow-write"]
    assert captured["kwargs"]["cwd"] == tmp_path
    assert captured["kwargs"]["stdout"] is managed_domshell.subprocess.DEVNULL
