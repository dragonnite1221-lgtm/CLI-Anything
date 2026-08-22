"""Tests for secure proxy lifecycle state validation."""

from __future__ import annotations

from contextlib import contextmanager
import json
import multiprocessing
import os

import pytest

from cli_anything.browser.utils import secure_egress_runtime as runtime


def _hold_startup_lock(runtime_path: str, acquired, release) -> None:
    os.environ[runtime.RUNTIME_ENV] = runtime_path
    with runtime._startup_lock():
        acquired.set()
        release.wait(5)


def _acquire_startup_lock(runtime_path: str, acquired) -> None:
    os.environ[runtime.RUNTIME_ENV] = runtime_path
    with runtime._startup_lock():
        acquired.set()


def test_private_runtime_state_is_loaded(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123, "identity": "12345"}), encoding="utf-8")
    state_path.chmod(0o600)

    assert runtime._load_state() == {"host": "127.0.0.1", "port": 4567, "pid": 123, "identity": "12345"}


def test_world_readable_runtime_state_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123, "identity": "12345"}), encoding="utf-8")
    state_path.chmod(0o644)

    assert runtime._load_state() is None


def test_running_proxy_requires_both_live_pid_and_loopback_listener(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123, "identity": "12345"}), encoding="utf-8")
    state_path.chmod(0o600)
    monkeypatch.setattr(runtime, "_alive", lambda state: state["pid"] == 123)

    assert runtime.running_proxy() == ("127.0.0.1", 4567)


def test_stop_proxy_never_signals_a_reused_pid(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    state_path = tmp_path / "secure-egress-proxy.json"
    state_path.write_text(json.dumps({"host": "127.0.0.1", "port": 4567, "pid": 123, "identity": "original"}), encoding="utf-8")
    state_path.chmod(0o600)
    signals: list[tuple[int, int]] = []
    monkeypatch.setattr(runtime, "_process_identity", lambda pid: "replacement")
    monkeypatch.setattr(runtime.os, "kill", lambda pid, signal: signals.append((pid, signal)))

    runtime.stop_proxy()

    assert signals == []
    assert not state_path.exists()


def test_existing_proxy_is_checked_under_the_startup_lock(monkeypatch):
    events: list[str] = []

    @contextmanager
    def lock():
        events.append("lock")
        yield
        events.append("unlock")

    monkeypatch.setattr(runtime, "_startup_lock", lock)
    monkeypatch.setattr(runtime, "running_proxy", lambda: events.append("check") or ("127.0.0.1", 4567))

    assert runtime.ensure_proxy() == ("127.0.0.1", 4567)
    assert events == ["lock", "check", "unlock"]


@pytest.mark.skipif(runtime.fcntl is None or "fork" not in multiprocessing.get_all_start_methods(), reason="requires Unix advisory locks")
def test_startup_lock_blocks_a_concurrent_process(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path))
    context = multiprocessing.get_context("fork")
    first_acquired, second_acquired, release = context.Event(), context.Event(), context.Event()
    holder = context.Process(target=_hold_startup_lock, args=(str(tmp_path), first_acquired, release))
    contender = context.Process(target=_acquire_startup_lock, args=(str(tmp_path), second_acquired))
    try:
        holder.start()
        assert first_acquired.wait(2)
        contender.start()
        assert not second_acquired.wait(0.2)
        release.set()
        assert second_acquired.wait(2)
    finally:
        release.set()
        holder.join(5)
        contender.join(5)
        if holder.is_alive():
            holder.terminate()
        if contender.is_alive():
            contender.terminate()
