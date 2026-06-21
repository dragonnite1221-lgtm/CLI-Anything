# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIArgParsing:
    """Verify Click argument/option parsing for each command group."""

    @patch.object(SeaClipBackend, "list_issues", return_value=[])
    def test_issue_list_with_filters(self, mock_list):
        result, _ = invoke_json(
            "issue", "list", "--status", "backlog", "--priority", "high", "--limit", "5"
        )
        assert result.exit_code == 0
        mock_list.assert_called_once_with(
            status="backlog", priority="high", search=None, limit=5
        )

    @patch.object(SeaClipBackend, "move_issue", return_value={"ok": True})
    def test_issue_move_requires_column(self, mock_move):
        result, data = invoke_json("issue", "move", "abc-123", "--column", "done")
        assert result.exit_code == 0
        mock_move.assert_called_once_with("abc-123", "done")

    def test_issue_move_missing_column_fails(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "issue", "move", "abc-123"])
        assert result.exit_code != 0

    @patch.object(SeaClipBackend, "start_pipeline", return_value={"started": True})
    def test_pipeline_start_mode(self, mock_start):
        result, data = invoke_json(
            "pipeline", "start", "--issue", "uuid-1", "--mode", "manual"
        )
        assert result.exit_code == 0
        mock_start.assert_called_once_with("uuid-1", mode="manual")

    def test_pipeline_start_invalid_mode(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--json", "pipeline", "start", "--issue", "x", "--mode", "bogus"]
        )
        assert result.exit_code != 0

    @patch.object(SeaClipBackend, "list_activity", return_value=[])
    def test_activity_default_limit(self, mock_act):
        result, _ = invoke_json("activity", "list")
        assert result.exit_code == 0
        mock_act.assert_called_once_with(limit=20)

    @patch.object(SeaClipBackend, "add_schedule", return_value={"id": 1})
    def test_scheduler_add_parsing(self, mock_add):
        result, data = invoke_json(
            "scheduler", "add", "--name", "nightly", "--cron", "0 2 * * *"
        )
        assert result.exit_code == 0
        mock_add.assert_called_once_with({"name": "nightly", "cron": "0 2 * * *"})


class TestErrorHandling:
    """Verify error paths produce JSON error objects and non-zero exit."""

    @patch.object(
        SeaClipBackend, "health", side_effect=ConnectionError("Connection refused")
    )
    def test_server_health_connection_error(self, mock_health):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "server", "health"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert "error" in data
        assert "Connection refused" in data["error"]

    @patch.object(SeaClipBackend, "list_issues", side_effect=Exception("timeout"))
    def test_issue_list_error(self, mock_list):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "issue", "list"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert "error" in data

    @patch.object(SeaClipBackend, "list_agents", side_effect=Exception("DB locked"))
    def test_agent_list_error(self, mock_agents):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "agent", "list"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert "DB locked" in data["error"]

    def test_unknown_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "nonexistent"])
        assert result.exit_code != 0

    def test_version_flag(self):
        result = invoke("--version")
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help_flag(self):
        result = invoke("--help")
        assert result.exit_code == 0
        assert "SeaClip-Lite CLI" in result.output
