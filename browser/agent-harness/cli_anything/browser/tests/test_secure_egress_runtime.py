"""Tests for secure proxy lifecycle state validation."""

from __future__ import annotations

import json

from cli_anything.browser.utils import secure_egress_runtime as runtime


def test_private_runtime_state_is_loaded(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123}), encoding="utf-8")
    state_path.chmod(0o600)

    assert runtime._load_state() == {"host": "127.0.0.1", "port": 4567, "pid": 123}


def test_world_readable_runtime_state_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123}), encoding="utf-8")
    state_path.chmod(0o644)

    assert runtime._load_state() is None


def test_running_proxy_requires_both_live_pid_and_loopback_listener(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123}), encoding="utf-8")
    state_path.chmod(0o600)
    monkeypatch.setattr(runtime, "_alive", lambda state: state["pid"] == 123)

    assert runtime.running_proxy() == ("127.0.0.1", 4567)
