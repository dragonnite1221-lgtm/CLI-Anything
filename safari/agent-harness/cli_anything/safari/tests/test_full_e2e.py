# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestDependencyChecks:
    """Verify dependency checking works with Safari MCP available."""

    def test_cli_help_works(self, runner):
        """--help must succeed even when Safari MCP is reachable."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Safari CLI" in result.output

    def test_cli_shows_all_command_groups(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        for group in ("tool", "tools", "raw", "session", "repl"):
            assert group in result.output


class TestSessionCommands:
    """Test session management via CliRunner."""

    def test_session_status_json(self, runner):
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "last_url" in data
        assert "current_tab_index" in data


class TestSecurityIntegration:
    """URL validation must block dangerous schemes at the CLI layer."""

    def test_file_url_blocked(self, runner):
        result = runner.invoke(cli, ["tool", "navigate", "--url", "file:///etc/passwd"])
        assert result.exit_code != 0
        assert "Blocked URL scheme" in result.output or "file" in result.output

    def test_javascript_url_blocked(self, runner):
        result = runner.invoke(
            cli, ["tool", "navigate", "--url", "javascript:alert(1)"]
        )
        assert result.exit_code != 0
        assert "Blocked" in result.output or "javascript" in result.output

    def test_about_url_blocked(self, runner):
        result = runner.invoke(cli, ["tool", "navigate", "--url", "about:blank"])
        assert result.exit_code != 0

    def test_missing_scheme_rejected(self, runner):
        result = runner.invoke(cli, ["tool", "navigate", "--url", "example.com"])
        assert result.exit_code != 0

    def test_raw_navigate_also_blocked(self, runner):
        """The raw escape hatch must also enforce URL validation."""
        result = runner.invoke(
            cli,
            ["raw", "safari_navigate", "--json-args", '{"url":"file:///etc/passwd"}'],
        )
        assert result.exit_code != 0


class TestRealSafariRoundTrip:
    """These tests actually talk to Safari. Only run when SAFARI_E2E=1."""

    def test_tab_list_returns_json(self, runner):
        """list-tabs should round-trip through safari-mcp and return valid JSON."""
        result = runner.invoke(cli, ["--json", "tool", "list-tabs"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data is not None

    def test_navigate_and_read_example_com(self, runner):
        """End-to-end navigation: open example.com and read title."""
        result = runner.invoke(
            cli, ["--json", "tool", "navigate-and-read", "--url", TEST_URL]
        )
        assert result.exit_code == 0
        assert "Example" in result.output or "example" in result.output
