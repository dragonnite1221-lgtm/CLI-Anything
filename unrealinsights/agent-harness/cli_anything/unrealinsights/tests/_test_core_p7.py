# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCLIJsonErrors:
    @patch("cli_anything.unrealinsights.unrealinsights_cli.resolve_unrealinsights_exe")
    def test_export_threads_requires_trace(self, _mock_resolve):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "export", "threads", "out.csv"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    @patch("cli_anything.unrealinsights.unrealinsights_cli.resolve_unrealinsights_exe")
    @patch("cli_anything.unrealinsights.unrealinsights_cli.resolve_trace_server_exe")
    def test_backend_info_json(self, mock_trace_server, mock_insights):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_insights.return_value = {
            "available": True,
            "path": "C:/UE/UnrealInsights.exe",
            "source": "explicit",
            "version": "5.5.4",
            "engine_version_hint": "5.5",
        }
        mock_trace_server.return_value = {
            "available": False,
            "path": None,
            "source": "unresolved",
            "version": None,
            "engine_version_hint": None,
            "error": "missing",
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "backend", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["insights"]["path"].endswith("UnrealInsights.exe")

    def test_capture_project_requires_engine_root(self, tmp_path):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        project = tmp_path / "MyGame.uproject"
        project.write_text("{}", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "capture", "run", "--project", str(project)])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "engine-root" in data["error"]

    @patch("cli_anything.unrealinsights.unrealinsights_cli.ensure_engine_unrealinsights")
    def test_backend_ensure_insights_json(self, mock_ensure):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_ensure.return_value = {
            "engine_root": "D:/UE_5.3",
            "insights": {
                "available": True,
                "path": "D:/UE_5.3/Engine/Binaries/Win64/UnrealInsights.exe",
                "source": "engine:UE_5.3",
                "version": "5.3.0",
                "engine_version_hint": None,
            },
            "trace_server": {
                "available": False,
                "path": None,
                "source": "unresolved",
                "version": None,
                "engine_version_hint": None,
                "error": "missing",
            },
            "build_attempted": False,
            "build": None,
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "backend", "ensure-insights", "--engine-root", "D:/UE_5.3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["insights"]["path"].endswith("UnrealInsights.exe")

    @patch("cli_anything.unrealinsights.unrealinsights_cli.capture_status")
    def test_capture_status_json(self, mock_capture_status):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_capture_status.return_value = {
            "active": True,
            "pid": 1234,
            "running": True,
            "target_exe": "C:/UE/UnrealEditor.exe",
            "target_args": [],
            "project_path": "C:/Project.uproject",
            "engine_root": "C:/UE_5.3",
            "trace_path": "C:/trace.utrace",
            "trace_exists": True,
            "trace_size": 1024,
            "channels": "default",
            "started_at": "2026-04-16T00:00:00+00:00",
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "capture", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["running"] is True

    @patch("cli_anything.unrealinsights.unrealinsights_cli.stop_capture")
    def test_capture_stop_json(self, mock_stop_capture):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_stop_capture.return_value = {
            "termination": {"requested_pid": 1234, "stopped": True, "exit_code": 0},
            "capture": {"active": False},
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "capture", "stop"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["termination"]["stopped"] is True

    @patch("cli_anything.unrealinsights.unrealinsights_cli.snapshot_capture")
    def test_capture_snapshot_json(self, mock_snapshot_capture):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_snapshot_capture.return_value = {
            "source_trace": "C:/trace.utrace",
            "snapshot_trace": "C:/trace-snapshot.utrace",
            "snapshot_exists": True,
            "snapshot_size": 2048,
            "capture_running": True,
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "capture", "snapshot"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["snapshot_exists"] is True

    @patch("cli_anything.unrealinsights.unrealinsights_cli.trace_store_info")
    def test_store_info_json(self, mock_store_info):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_store_info.return_value = {
            "trace_root": "C:/Trace",
            "trace_root_exists": True,
            "store_dir": "C:/Trace/Store",
            "store_exists": True,
            "trace_file_count": 0,
            "trace_server": {"available": False, "error": "missing"},
            "watch_folders": ["C:/Trace/Store"],
            "server_logs": [],
        }
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "store", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["store_exists"] is True

    def test_live_exec_json_backend_unavailable(self, monkeypatch):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        monkeypatch.delenv("UNREALINSIGHTS_LIVE_EXEC", raising=False)
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "live", "exec", "--pid", "1234", "Trace.Status"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "Live control backend unavailable" in data["error"]

    @patch("cli_anything.unrealinsights.unrealinsights_cli.gui_status")
    def test_gui_status_json(self, mock_gui_status):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        mock_gui_status.return_value = {"running": False, "process_count": 0, "processes": []}
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "gui", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["running"] is False

    def test_analyze_summary_skip_export_json(self, tmp_path):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        (tmp_path / "timer_stats.csv").write_text("Timer Name,Total Time\nTick,1.0\n", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "analyze", "summary", "--skip-export", "--out", str(tmp_path)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["summary"]["top_timers"][0]["name"] == "Tick"
