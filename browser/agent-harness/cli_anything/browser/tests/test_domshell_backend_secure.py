"""Regression tests that the backend cannot revive the legacy unmanaged path."""

from __future__ import annotations

from cli_anything.browser.utils import domshell_backend as backend


def test_server_command_uses_verified_local_binary_and_managed_secret(monkeypatch):
    monkeypatch.setattr(backend.managed_domshell, "ensure_managed_domshell", lambda: (3456, "managed-token"))
    monkeypatch.setattr(
        backend.domshell_runtime,
        "command",
        lambda binary, *args: ["node", f"/verified/{binary}.js", *args],
    )

    assert backend._build_server_command() == [
        "node",
        "/verified/domshell-proxy.js",
        "--port",
        "3456",
        "--token",
        "managed-token",
    ]


def test_availability_fails_closed_when_managed_runtime_cannot_start(monkeypatch):
    def fail():
        raise backend.managed_domshell.ManagedDOMShellError("extension is not configured")

    monkeypatch.setattr(backend.managed_domshell, "ensure_managed_domshell", fail)
    monkeypatch.setattr(backend.domshell_runtime, "status", lambda: {"installed": True})

    available, message = backend.is_available()

    assert not available
    assert message == "extension is not configured"


def test_mcp_subprocess_environment_omits_ambient_domshell_token(monkeypatch):
    monkeypatch.setenv("DOMSHELL_TOKEN", "legacy-token")
    monkeypatch.setattr(backend, "_build_server_command", lambda: ["node", "/verified/domshell-proxy.js"])

    parameters = backend._server_parameters()

    assert parameters.env is not None
    assert "DOMSHELL_TOKEN" not in parameters.env
    assert parameters.command == "node"
    assert parameters.args == ["/verified/domshell-proxy.js"]
