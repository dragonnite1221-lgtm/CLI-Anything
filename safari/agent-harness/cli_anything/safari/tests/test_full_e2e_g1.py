# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    """Invoke the installed CLI command as a real user/agent would.

    This class is required by HARNESS.md Phase 5: tests must exercise the
    actual installed `cli-anything-safari` command via subprocess, not just
    source imports via CliRunner. ``CLI_BASE`` is a cached class property
    rather than a class attribute so pytest collection does not call
    ``_resolve_cli`` (which can raise when ``CLI_ANYTHING_FORCE_INSTALLED=1``
    is set but the command is not in PATH).
    """

    _cli_base: "list[str] | None" = None

    @property
    def CLI_BASE(self) -> list[str]:
        base = type(self)._cli_base
        if base is None:
            base = _resolve_cli("cli-anything-safari")
            type(self)._cli_base = base
        return base

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "Safari CLI" in result.stdout

    def test_tool_group_help(self):
        result = self._run(["tool", "--help"])
        assert result.returncode == 0
        # Spot-check short names from each category — these are the MCP
        # tool names with the safari_ prefix stripped, so they're stable.
        for short in (
            "navigate",
            "snapshot",
            "click",
            "fill",
            "screenshot",
            "evaluate",
            "list-tabs",
            "mock-route",
        ):
            assert short in result.stdout, f"missing '{short}' in tool --help"

    def test_tools_count_is_84(self):
        result = self._run(["tools", "count"])
        assert result.returncode == 0
        assert result.stdout.strip() == "84"

    def test_tools_describe_scroll(self):
        result = self._run(["tools", "describe", "safari_scroll"])
        assert result.returncode == 0
        assert "direction" in result.stdout
        assert "amount" in result.stdout

    def test_tool_scroll_help_uses_schema(self):
        """Verify the auto-generated command matches the MCP schema exactly."""
        result = self._run(["tool", "scroll", "--help"])
        assert result.returncode == 0
        assert "--direction" in result.stdout
        assert "--amount" in result.stdout
        assert "up|down" in result.stdout  # enum choices

    def test_raw_help(self):
        result = self._run(["raw", "--help"])
        assert result.returncode == 0
        assert "tool_name" in result.stdout.lower()

    def test_session_status_json(self):
        result = self._run(["--json", "session", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "last_url" in data
        assert "current_tab_index" in data

    def test_blocked_scheme_exits_nonzero(self):
        # Note: check=False because we expect non-zero exit
        result = self._run(
            ["tool", "navigate", "--url", "file:///etc/passwd"], check=False
        )
        assert result.returncode != 0

    def test_list_tabs_json_roundtrip(self):
        """End-to-end: installed CLI → safari-mcp → Safari → back."""
        result = self._run(["--json", "tool", "list-tabs"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data is not None
        print(f"\n  list-tabs: {len(data) if isinstance(data, list) else 'n/a'} tabs")
