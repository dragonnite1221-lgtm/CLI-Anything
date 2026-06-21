# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCaptureCLIConvenienceMixin1:
    @patch("cli_anything.unrealinsights.unrealinsights_cli.capture_status")
    @patch("cli_anything.unrealinsights.unrealinsights_cli.run_capture")
    def test_capture_start_refuses_running_session_without_replace(self, mock_run_capture, mock_capture_status):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_capture_status.return_value = {
            "active": True,
            "pid": 1357,
            "running": True,
            "target_exe": "C:/UE/UnrealEditor.exe",
            "target_args": [],
            "project_path": "C:/Project.uproject",
            "engine_root": "C:/UE_5.5",
            "trace_path": "C:/capture.utrace",
            "trace_exists": True,
            "trace_size": 1024,
            "channels": "default",
            "started_at": "2026-04-16T00:00:00+00:00",
        }

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--json",
                "capture",
                "start",
                "--project",
                "C:/Project.uproject",
                "--engine-root",
                "C:/UE_5.5",
            ],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "--replace" in data["error"]
        mock_run_capture.assert_not_called()
    @patch("cli_anything.unrealinsights.unrealinsights_cli.stop_capture")
    @patch("cli_anything.unrealinsights.unrealinsights_cli.capture_status")
    @patch("cli_anything.unrealinsights.unrealinsights_cli.run_capture")
    def test_capture_start_replace_stops_existing_session(self, mock_run_capture, mock_capture_status, mock_stop_capture, tmp_path):
        from cli_anything.unrealinsights.unrealinsights_cli import cli
        from cli_anything.unrealinsights.core.session import UnrealInsightsSession

        editor = tmp_path / "UE_5.5" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        editor.parent.mkdir(parents=True)
        editor.write_text("x", encoding="utf-8")
        project = tmp_path / "Project" / "MyGame.uproject"
        project.parent.mkdir(parents=True)
        project.write_text("{}", encoding="utf-8")

        mock_capture_status.return_value = {
            "active": True,
            "pid": 1357,
            "running": True,
            "target_exe": str(editor.resolve()),
            "target_args": [str(project.resolve())],
            "project_path": str(project.resolve()),
            "engine_root": str((tmp_path / "UE_5.5").resolve()),
            "trace_path": str((tmp_path / "previous.utrace").resolve()),
            "trace_exists": True,
            "trace_size": 1024,
            "channels": "default",
            "started_at": "2026-04-16T00:00:00+00:00",
        }
        mock_stop_capture.return_value = {
            "termination": {"requested_pid": 1357, "stopped": True, "exit_code": 0},
            "capture": {"active": False},
        }
        mock_run_capture.return_value = {
            "command": [str(editor.resolve()), str(project.resolve()), "-trace=default"],
            "waited": False,
            "timed_out": False,
            "exit_code": None,
            "stdout": None,
            "stderr": None,
            "pid": 2468,
            "target_exe": str(editor.resolve()),
            "target_args": [str(project.resolve())],
            "trace_path": str((tmp_path / "capture.utrace").resolve()),
            "channels": "default",
            "trace_exists": False,
            "trace_size": None,
            "succeeded": True,
        }

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--json",
                "capture",
                "start",
                "--replace",
                "--project",
                str(project),
                "--engine-root",
                str(tmp_path / "UE_5.5"),
                "--output-trace",
                str(tmp_path / "capture.utrace"),
            ],
        )
        assert result.exit_code == 0
        mock_stop_capture.assert_called_once()
        session = UnrealInsightsSession.load()
        assert session.capture_pid == 2468
