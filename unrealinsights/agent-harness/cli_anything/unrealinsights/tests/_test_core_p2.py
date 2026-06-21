# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCaptureCore:
    def test_normalize_trace_output_path_prefers_explicit(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import normalize_trace_output_path

        path = normalize_trace_output_path("game.exe", output_trace=str(tmp_path / "capture"))
        assert path.endswith(".utrace")

    def test_build_exec_cmds_arg(self):
        from cli_anything.unrealinsights.core.capture import build_exec_cmds_arg

        assert build_exec_cmds_arg(["Trace.Bookmark Boot", "Trace.RegionBegin Boot"]) == (
            "Trace.Bookmark Boot,Trace.RegionBegin Boot"
        )

    def test_resolve_engine_root_from_engine_subdir(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import resolve_engine_root

        engine_dir = tmp_path / "UE_5.5" / "Engine"
        engine_dir.mkdir(parents=True)
        assert resolve_engine_root(str(engine_dir)) == str((tmp_path / "UE_5.5").resolve())

    def test_resolve_editor_target(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import resolve_editor_target

        editor = tmp_path / "UE_5.5" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        editor.parent.mkdir(parents=True)
        editor.write_text("x", encoding="utf-8")
        assert resolve_editor_target(str(tmp_path / "UE_5.5")) == str(editor.resolve())

    def test_resolve_capture_target_from_project_and_engine(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import resolve_capture_target

        editor = tmp_path / "UE_5.5" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        editor.parent.mkdir(parents=True)
        editor.write_text("x", encoding="utf-8")
        project = tmp_path / "Project" / "MyGame.uproject"
        project.parent.mkdir(parents=True)
        project.write_text("{}", encoding="utf-8")

        target_exe, target_args, launch_info = resolve_capture_target(
            None,
            project=str(project),
            engine_root=str(tmp_path / "UE_5.5"),
            target_args=["-game"],
        )
        assert target_exe == str(editor.resolve())
        assert target_args[0] == str(project.resolve())
        assert "-game" in target_args
        assert launch_info["project_path"] == str(project.resolve())

    def test_build_capture_command(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import build_capture_command

        exe = tmp_path / "Game.exe"
        exe.write_text("x", encoding="utf-8")
        trace = tmp_path / "capture.utrace"
        command = build_capture_command(
            str(exe),
            str(trace),
            channels="default,bookmark",
            exec_cmds=["Trace.Bookmark Boot"],
            target_args=["MyGame.uproject", "-game"],
        )
        assert command[0] == str(exe.resolve())
        assert "MyGame.uproject" in command
        assert "-trace=default,bookmark" in command
        assert any(arg.startswith("-tracefile=") for arg in command)
        assert any(arg.startswith("-ExecCmds=") for arg in command)

    @patch("cli_anything.unrealinsights.core.capture.backend.run_process")
    def test_run_capture_wait_requires_clean_exit(self, mock_run_process, tmp_path):
        from cli_anything.unrealinsights.core.capture import run_capture

        exe = tmp_path / "Game.exe"
        exe.write_text("x", encoding="utf-8")
        trace = tmp_path / "capture.utrace"
        trace.write_text("partial-trace", encoding="utf-8")

        mock_run_process.return_value = {
            "command": [str(exe.resolve())],
            "waited": True,
            "timed_out": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "boom",
            "pid": None,
        }

        result = run_capture(str(exe), str(trace), wait=True)
        assert result["trace_exists"] is True
        assert result["succeeded"] is False

    def test_capture_status(self):
        from cli_anything.unrealinsights.core.capture import capture_status
        from cli_anything.unrealinsights.core.session import UnrealInsightsSession

        session = UnrealInsightsSession()
        session.set_capture(
            pid=1234,
            target_exe="C:/UE/UnrealEditor.exe",
            target_args=["Project.uproject"],
            trace_path="C:/trace.utrace",
            channels="default",
        )
        with patch("cli_anything.unrealinsights.core.capture.backend.is_process_running", return_value=True):
            data = capture_status(session)
        assert data["active"] is True
        assert data["running"] is True

    def test_snapshot_capture(self, tmp_path):
        from cli_anything.unrealinsights.core.capture import snapshot_capture
        from cli_anything.unrealinsights.core.session import UnrealInsightsSession

        trace = tmp_path / "live.utrace"
        trace.write_text("trace-data", encoding="utf-8")
        session = UnrealInsightsSession()
        session.set_capture(
            pid=4321,
            target_exe="C:/UE/UnrealEditor.exe",
            target_args=[],
            trace_path=str(trace),
            channels="default",
        )
        with patch("cli_anything.unrealinsights.core.capture.backend.is_process_running", return_value=True):
            result = snapshot_capture(session)
        assert Path(result["snapshot_trace"]).is_file()

    def test_stop_capture(self):
        from cli_anything.unrealinsights.core.capture import stop_capture
        from cli_anything.unrealinsights.core.session import UnrealInsightsSession

        session = UnrealInsightsSession()
        session.set_capture(
            pid=9876,
            target_exe="C:/UE/UnrealEditor.exe",
            target_args=[],
            trace_path="C:/trace.utrace",
            channels="default",
        )
        with patch("cli_anything.unrealinsights.core.capture.backend.terminate_process", return_value={"requested_pid": 9876, "stopped": True, "exit_code": 0}), \
             patch("cli_anything.unrealinsights.core.capture.backend.is_process_running", return_value=False):
            result = stop_capture(session)
        assert result["termination"]["stopped"] is True
