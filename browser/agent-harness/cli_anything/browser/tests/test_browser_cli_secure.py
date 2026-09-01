"""CLI tests for the secure runtime controls."""

from __future__ import annotations

from click.testing import CliRunner

from cli_anything.browser import browser_cli


def test_secure_status_does_not_start_browser(monkeypatch):
    monkeypatch.setattr(browser_cli.backend, "secure_runtime_status", lambda: {"managed": False})
    monkeypatch.setattr(
        browser_cli.backend,
        "is_available",
        lambda: (_ for _ in ()).throw(AssertionError("status must not start the runtime")),
    )

    result = CliRunner().invoke(browser_cli.cli, ["--json", "secure", "status"])

    assert result.exit_code == 0
    assert result.output.strip() == '{\n  "managed": false\n}'


def test_secure_stop_stops_daemon_and_managed_runtime(monkeypatch):
    stopped: list[str] = []
    monkeypatch.setattr(browser_cli.backend, "stop_daemon", lambda: stopped.append("daemon"))
    monkeypatch.setattr(browser_cli.backend, "stop_secure_runtime", lambda: stopped.append("runtime"))

    result = CliRunner().invoke(browser_cli.cli, ["secure", "stop"])

    assert result.exit_code == 0
    assert stopped == ["daemon", "runtime"]
