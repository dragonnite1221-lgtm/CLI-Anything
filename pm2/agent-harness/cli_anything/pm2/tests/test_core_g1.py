# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProcesses:
    """Tests for process listing, describe, and metrics."""

    @patch("cli_anything.pm2.core.processes.pm2_jlist")
    def test_list_processes_json(self, mock_jlist):
        mock_jlist.return_value = json.loads(FAKE_JLIST)
        from cli_anything.pm2.core.processes import list_processes

        result = list_processes(as_json=True)
        assert isinstance(result, list)
        assert len(result) == 2

    @patch("cli_anything.pm2.core.processes.pm2_jlist")
    def test_list_processes_human(self, mock_jlist):
        mock_jlist.return_value = json.loads(FAKE_JLIST)
        from cli_anything.pm2.core.processes import list_processes

        result = list_processes(as_json=False)
        assert isinstance(result, list)
        assert result[0]["name"] == "seaclip-dev"
        assert result[0]["status"] == "online"

    @patch("cli_anything.pm2.core.processes.pm2_jlist")
    def test_list_processes_empty(self, mock_jlist):
        mock_jlist.return_value = []
        from cli_anything.pm2.core.processes import list_processes

        result = list_processes(as_json=False)
        assert result == "No PM2 processes running."

    @patch("cli_anything.pm2.core.processes.pm2_describe")
    def test_describe_process_found(self, mock_desc):
        mock_desc.return_value = json.loads(FAKE_JLIST)[0]
        from cli_anything.pm2.core.processes import describe_process

        result = describe_process("seaclip-dev", as_json=False)
        assert isinstance(result, dict)
        assert result["Name"] == "seaclip-dev"

    @patch("cli_anything.pm2.core.processes.pm2_describe")
    def test_describe_process_not_found(self, mock_desc):
        mock_desc.return_value = None
        from cli_anything.pm2.core.processes import describe_process

        result = describe_process("ghost", as_json=False)
        assert result is None

    @patch("cli_anything.pm2.core.processes.pm2_jlist")
    def test_get_metrics_json(self, mock_jlist):
        mock_jlist.return_value = json.loads(FAKE_JLIST)
        from cli_anything.pm2.core.processes import get_metrics

        result = get_metrics(as_json=True)
        assert isinstance(result, list)
        assert result[0]["cpu"] == 2.5


class TestLifecycle:
    """Tests for lifecycle commands."""

    @patch("cli_anything.pm2.core.lifecycle.pm2_action")
    def test_restart_success(self, mock_action):
        mock_action.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "restarted",
            "stderr": "",
        }
        from cli_anything.pm2.core.lifecycle import restart_process

        result = restart_process("seaclip-dev", as_json=False)
        assert result["success"] is True
        assert "Restarted" in result["message"]

    @patch("cli_anything.pm2.core.lifecycle.pm2_action")
    def test_stop_failure(self, mock_action):
        mock_action.return_value = {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": "process not found",
        }
        from cli_anything.pm2.core.lifecycle import stop_process

        result = stop_process("ghost", as_json=False)
        assert result["success"] is False
        assert "Failed" in result["message"]

    @patch("cli_anything.pm2.core.lifecycle.backend_start")
    def test_start_with_name(self, mock_start):
        mock_start.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "started",
            "stderr": "",
        }
        from cli_anything.pm2.core.lifecycle import start_process

        result = start_process("/app/index.js", name="my-app", as_json=True)
        assert result["success"] is True
        assert result["name"] == "my-app"


class TestLogs:
    """Tests for log commands."""

    @patch("cli_anything.pm2.core.logs.backend_logs")
    def test_view_logs_success(self, mock_logs):
        mock_logs.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "line1\nline2\n",
            "stderr": "",
        }
        from cli_anything.pm2.core.logs import view_logs

        result = view_logs("seaclip-dev", lines=20, as_json=False)
        assert result["success"] is True
        assert "line1" in result["content"]

    @patch("cli_anything.pm2.core.logs.backend_flush")
    def test_flush_all(self, mock_flush):
        mock_flush.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "flushed",
            "stderr": "",
        }
        from cli_anything.pm2.core.logs import flush_logs

        result = flush_logs(name=None, as_json=False)
        assert result["success"] is True
        assert "all processes" in result["message"]
