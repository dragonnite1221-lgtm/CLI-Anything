# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestLiveCore:
    @patch("cli_anything.unrealinsights.core.live.subprocess.run")
    def test_list_unreal_processes_windows_json(self, mock_run):
        from cli_anything.unrealinsights.core.live import list_unreal_processes

        mock_run.return_value = type(
            "Result",
            (),
            {
                "returncode": 0,
                "stdout": json.dumps(
                    [
                        {
                            "Name": "UnrealEditor.exe",
                            "ProcessId": 100,
                            "ExecutablePath": "C:/UE/UnrealEditor.exe",
                            "CommandLine": "UnrealEditor.exe C:/Game.uproject",
                            "CreationDate": "now",
                        },
                        {
                            "Name": "UnrealInsights.exe",
                            "ProcessId": 200,
                            "ExecutablePath": "C:/UE/UnrealInsights.exe",
                            "CommandLine": "UnrealInsights.exe",
                            "CreationDate": "now",
                        },
                        {
                            "Name": "CustomUnrealHost.exe",
                            "ProcessId": 300,
                            "ExecutablePath": "C:/Tools/CustomUnrealHost.exe",
                            "CommandLine": "CustomUnrealHost.exe",
                            "CreationDate": "now",
                        },
                    ]
                ),
            },
        )()

        with patch("cli_anything.unrealinsights.core.live.os.name", "nt"):
            result = list_unreal_processes()
        assert result["process_count"] == 3
        assert {process["role"] for process in result["processes"]} == {"editor", "insights", "unknown"}

        with patch("cli_anything.unrealinsights.core.live.os.name", "nt"):
            no_tools = list_unreal_processes(include_tools=False)
        assert {process["role"] for process in no_tools["processes"]} == {"editor", "unknown"}

    def test_live_exec_requires_backend(self, monkeypatch):
        from cli_anything.unrealinsights.core.live import execute_live_command

        monkeypatch.delenv("UNREALINSIGHTS_LIVE_EXEC", raising=False)
        with pytest.raises(RuntimeError, match="Live control backend unavailable"):
            execute_live_command(100, "Trace.Status", backend_command=None)

    @patch("cli_anything.unrealinsights.core.live.backend.run_process")
    def test_live_exec_uses_template(self, mock_run, monkeypatch):
        from cli_anything.unrealinsights.core.live import execute_live_command

        monkeypatch.delenv("UNREALINSIGHTS_LIVE_EXEC", raising=False)
        mock_run.return_value = {
            "command": ["sender"],
            "waited": True,
            "timed_out": False,
            "exit_code": 0,
            "stdout": "ok",
            "stderr": "",
            "pid": None,
        }

        result = execute_live_command(100, "Trace.Status", backend_command='sender --pid {pid} --cmd "{cmd}"')
        assert result["succeeded"] is True
        assert result["live_command"] == "Trace.Status"


class TestGuiCore:
    def test_build_gui_command_has_no_headless_flags(self, tmp_path):
        from cli_anything.unrealinsights.core.gui import build_gui_command

        exe = tmp_path / "UnrealInsights.exe"
        trace = tmp_path / "session.utrace"
        exe.write_text("x", encoding="utf-8")
        trace.write_text("x", encoding="utf-8")
        command = build_gui_command(str(exe), str(trace))
        assert "-NoUI" not in command
        assert "-AutoQuit" not in command
        assert any(arg.startswith("-OpenTraceFile=") for arg in command)

    @patch("cli_anything.unrealinsights.core.gui.backend.run_process")
    def test_open_gui_keeps_running(self, mock_run, tmp_path):
        from cli_anything.unrealinsights.core.gui import open_gui

        exe = tmp_path / "UnrealInsights.exe"
        exe.write_text("x", encoding="utf-8")
        mock_run.return_value = {
            "command": [str(exe)],
            "waited": False,
            "timed_out": False,
            "exit_code": None,
            "stdout": None,
            "stderr": None,
            "pid": 321,
        }
        result = open_gui(str(exe))
        assert result["pid"] == 321
        assert result["kept_running"] is True
