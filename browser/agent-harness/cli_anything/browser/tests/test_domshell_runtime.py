"""Regression tests for the local lockfile-pinned DOMShell runtime."""

from __future__ import annotations

import json

import pytest

from cli_anything.browser.utils import domshell_runtime as runtime


def test_command_fails_closed_when_local_runtime_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(tmp_path / "missing"))

    with pytest.raises(runtime.DOMShellRuntimeError, match="not installed"):
        runtime.command("domshell")


def test_install_refuses_a_nonempty_unmanaged_directory(monkeypatch, tmp_path):
    root = tmp_path / "another-project"
    root.mkdir(mode=0o700)
    (root / "package.json").write_text('{"name":"another-project"}', encoding="utf-8")
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(root))

    with pytest.raises(runtime.DOMShellRuntimeError, match="not managed"):
        runtime.install()


def test_command_uses_only_verified_local_node_script(monkeypatch, tmp_path):
    root = tmp_path / "runtime"
    package = root / "node_modules" / "@apireno" / "domshell"
    (package / "bin").mkdir(parents=True)
    root.chmod(0o700)
    lock = b'{"lockfileVersion":3}'
    (root / "package-lock.json").write_bytes(lock)
    (root / "package-lock.json").chmod(0o600)
    (root / runtime.RUNTIME_MARKER).write_bytes(runtime.RUNTIME_MARKER_CONTENT)
    (root / runtime.RUNTIME_MARKER).chmod(0o600)
    (root / runtime.INSTALL_MARKER).write_bytes(runtime.INSTALL_MARKER_CONTENT)
    (root / runtime.INSTALL_MARKER).chmod(0o600)
    (package / "package.json").write_text(
        json.dumps({"name": runtime.PACKAGE_NAME, "version": runtime.PACKAGE_VERSION}),
        encoding="utf-8",
    )
    (package / "bin" / "domshell.js").write_text("", encoding="utf-8")
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(root))
    monkeypatch.setattr(runtime, "_bundled_file", lambda name: lock if name == "package-lock.json" else b"{}")
    monkeypatch.setattr(runtime, "_node", lambda: "/usr/bin/node")

    assert runtime.command("domshell", "--granular") == [
        "/usr/bin/node",
        str(package / "bin" / "domshell.js"),
        "--granular",
    ]


def test_command_rejects_an_incomplete_runtime_install(monkeypatch, tmp_path):
    root = tmp_path / "runtime"
    root.mkdir(mode=0o700)
    (root / runtime.RUNTIME_MARKER).write_bytes(runtime.RUNTIME_MARKER_CONTENT)
    (root / runtime.RUNTIME_MARKER).chmod(0o600)
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(root))

    with pytest.raises(runtime.DOMShellRuntimeError, match="not installed|incomplete"):
        runtime.command("domshell")


def test_status_rejects_group_readable_runtime_directory(monkeypatch, tmp_path):
    root = tmp_path / "runtime"
    root.mkdir()
    root.chmod(0o755)
    monkeypatch.setenv(runtime.RUNTIME_ENV, str(root))

    assert runtime.status()["installed"] is False


def test_node_requires_the_runtime_minimum_version(monkeypatch):
    class Completed:
        stdout = "v16.20.2\n"

    monkeypatch.setattr(runtime.shutil, "which", lambda binary: "/usr/bin/node")
    monkeypatch.setattr(runtime.subprocess, "run", lambda *_args, **_kwargs: Completed())

    with pytest.raises(runtime.DOMShellRuntimeError, match="18 or later"):
        runtime._node()


def test_install_checks_node_before_invoking_npm(monkeypatch):
    monkeypatch.setattr(runtime, "_node", lambda: (_ for _ in ()).throw(runtime.DOMShellRuntimeError("old Node")))

    with pytest.raises(runtime.DOMShellRuntimeError, match="old Node"):
        runtime.install()
