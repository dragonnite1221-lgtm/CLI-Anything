# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCaptureCLIConvenienceMixin0:
    @patch("cli_anything.unrealinsights.unrealinsights_cli.run_capture")
    def test_capture_run_with_project_and_engine_root(self, mock_run_capture, tmp_path):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        editor = tmp_path / "UE_5.5" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        editor.parent.mkdir(parents=True)
        editor.write_text("x", encoding="utf-8")
        project = tmp_path / "Project" / "MyGame.uproject"
        project.parent.mkdir(parents=True)
        project.write_text("{}", encoding="utf-8")

        mock_run_capture.return_value = {
            "command": [str(editor.resolve()), str(project.resolve()), "-trace=default"],
            "waited": True,
            "timed_out": False,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "pid": None,
            "target_exe": str(editor.resolve()),
            "target_args": [str(project.resolve())],
            "trace_path": str((tmp_path / "capture.utrace").resolve()),
            "channels": "default",
            "trace_exists": True,
            "trace_size": 10,
            "succeeded": True,
        }

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--json",
                "capture",
                "run",
                "--project",
                str(project),
                "--engine-root",
                str(tmp_path / "UE_5.5"),
                "--output-trace",
                str(tmp_path / "capture.utrace"),
                "--wait",
            ],
        )
        assert result.exit_code == 0
        mock_run_capture.assert_called_once()
        _, kwargs = mock_run_capture.call_args
        assert kwargs["target_args"][0] == str(project.resolve())
    @patch("cli_anything.unrealinsights.unrealinsights_cli.run_capture")
    def test_capture_start_persists_background_session(self, mock_run_capture, tmp_path):
        from cli_anything.unrealinsights.unrealinsights_cli import cli
        from cli_anything.unrealinsights.core.session import UnrealInsightsSession

        editor = tmp_path / "UE_5.5" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        editor.parent.mkdir(parents=True)
        editor.write_text("x", encoding="utf-8")
        project = tmp_path / "Project" / "MyGame.uproject"
        project.parent.mkdir(parents=True)
        project.write_text("{}", encoding="utf-8")

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
                "--project",
                str(project),
                "--engine-root",
                str(tmp_path / "UE_5.5"),
                "--output-trace",
                str(tmp_path / "capture.utrace"),
            ],
        )
        assert result.exit_code == 0
        session = UnrealInsightsSession.load()
        assert session.capture_pid == 2468
