"""Unit tests for the helper process used only inside the isolated browser namespace."""

from __future__ import annotations

from cli_anything.browser.utils import managed_domshell_browser


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

    monkeypatch.setattr(managed_domshell_browser.shutil, "which", lambda _name: str(executable))
    monkeypatch.setattr(managed_domshell_browser.subprocess, "run", fake_run)
    monkeypatch.setattr(managed_domshell_browser.secure_egress_runtime, "runtime_dir", lambda: tmp_path)

    managed_domshell_browser._agent_browser("127.0.0.1", 45123, tmp_path, 49876, ["open", "about:blank"])

    command = captured["command"]
    assert "--headless=new,--remote-allow-origins=http://localhost,--disable-quic,--force-webrtc-ip-handling-policy=disable_non_proxied_udp" in command
    assert "<-loopback>,127.0.0.1:49876" in command


def test_mcp_server_requests_granular_tools(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    class Process:
        pid = 123

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return Process()

    monkeypatch.setattr(managed_domshell_browser.secure_egress_runtime, "runtime_dir", lambda: tmp_path)
    monkeypatch.setattr(managed_domshell_browser.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(managed_domshell_browser.domshell_runtime, "command", lambda binary: ["node", f"/verified/{binary}.js"])

    managed_domshell_browser._start_mcp_server("test-token", 3456, 4567)

    assert captured["command"][:2] == ["node", "/verified/domshell.js"]
    assert captured["command"][-2:] == ["--granular", "--allow-write"]
    assert captured["kwargs"]["cwd"] == tmp_path
    assert captured["kwargs"]["stdout"] is managed_domshell_browser.subprocess.DEVNULL
