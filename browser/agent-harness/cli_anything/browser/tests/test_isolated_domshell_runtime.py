"""Regression tests for the private network namespace launcher."""

from __future__ import annotations

import json

import pytest

from cli_anything.browser.utils import isolated_domshell_runner as runner
from cli_anything.browser.utils import isolated_domshell_runtime as runtime


def test_isolation_requires_all_host_tools(monkeypatch):
    monkeypatch.setattr(runtime.shutil, "which", lambda _name: None)

    with pytest.raises(runtime.ManagedDOMShellError, match="uidmap"):
        runtime._isolation_tools()


def test_isolation_fails_before_startup_on_non_linux_hosts(monkeypatch):
    monkeypatch.setattr(runtime.sys, "platform", "darwin")

    with pytest.raises(runtime.ManagedDOMShellError, match="only on Linux"):
        runtime._isolation_tools()


def test_launcher_publishes_only_the_authenticated_mcp_port(monkeypatch, tmp_path):
    class Process:
        def poll(self):
            return None

    captured: dict[str, object] = {}

    def fake_popen(command, **_kwargs):
        captured["command"] = command
        ready_path = command[command.index("--ready-path") + 1]
        path = tmp_path / "isolated-domshell-ready.json"
        assert str(path) == ready_path
        path.write_text(json.dumps({"ready": True, "identity": "123"}), encoding="utf-8")
        path.chmod(0o600)
        return Process()

    monkeypatch.setattr(runtime, "runtime_dir", lambda: tmp_path)
    monkeypatch.setattr(runtime, "_isolation_tools", lambda: ("/usr/bin/rootlesskit", "/usr/bin/slirp4netns", "/usr/bin/newuidmap"))
    monkeypatch.setattr(runtime.subprocess, "Popen", fake_popen)

    process = runtime.start_isolated_runtime(tmp_path / "extension", "secret", 3456, 4567)

    assert isinstance(process, Process)
    command = captured["command"]
    assert "--disable-host-loopback" in command
    assert command[command.index("--publish") + 1] == "127.0.0.1:3456:3456/tcp"
    assert "4567" not in command


def test_launcher_removes_private_token_config_when_spawn_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime, "runtime_dir", lambda: tmp_path)
    monkeypatch.setattr(runtime, "_isolation_tools", lambda: ("/usr/bin/rootlesskit", "/usr/bin/slirp4netns", "/usr/bin/newuidmap"))

    def fail_popen(*_args, **_kwargs):
        raise OSError("launcher unavailable")

    monkeypatch.setattr(runtime.subprocess, "Popen", fail_popen)

    with pytest.raises(runtime.ManagedDOMShellError, match="could not launch"):
        runtime.start_isolated_runtime(tmp_path / "extension", "secret", 3456, 4567)

    assert not (tmp_path / "isolated-domshell-config.json").exists()


def test_runner_rejects_non_private_configuration(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"token": "secret"}), encoding="utf-8")
    config.chmod(0o644)

    with pytest.raises(RuntimeError, match="invalid"):
        runner._private_json(config)
