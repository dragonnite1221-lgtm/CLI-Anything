# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestAnalyzeCore:
    def test_summarize_exports_from_synthetic_csv(self, tmp_path):
        from cli_anything.unrealinsights.core.analyze import summarize_exports

        (tmp_path / "timer_stats.csv").write_text(
            "\n".join(
                [
                    "Timer Name,Thread,Total Time,Count",
                    "Tick,GameThread,12.5,3",
                    "WaitForTasks,RenderThread,20.0,2",
                ]
            ),
            encoding="utf-8",
        )
        (tmp_path / "counter_values.csv").write_text(
            "\n".join(
                [
                    "Counter,Value",
                    "FrameTime,33.3",
                    "FrameTime,16.6",
                ]
            ),
            encoding="utf-8",
        )

        result = summarize_exports(str(tmp_path), limit=2)
        assert result["succeeded"] is True
        assert result["summary"]["top_timers"][0]["name"] == "WaitForTasks"
        assert result["summary"]["focus_threads"]["GameThread"][0]["name"] == "Tick"
        assert result["summary"]["counter_peaks"][0]["name"] == "FrameTime"
        diagnostics = result["summary"]["diagnostics"]
        assert diagnostics["primary_hotspot"]["name"] == "WaitForTasks"
        assert diagnostics["wait_pressure"] == "present"
        assert diagnostics["counter_anomaly_count"] == 1

    def test_summarize_exports_reports_export_status(self, tmp_path):
        from cli_anything.unrealinsights.core.analyze import summarize_exports

        (tmp_path / "timer_stats.csv").write_text("Timer Name,Total Time\nTick,1.0\n", encoding="utf-8")
        result = summarize_exports(
            str(tmp_path),
            export_results=[
                {
                    "exporter": "timer-stats",
                    "output_status": "ok",
                    "succeeded": True,
                    "output_files": [str(tmp_path / "timer_stats.csv")],
                    "status_message": "ok",
                    "log_path": "timer_stats.log",
                },
                {
                    "exporter": "counter-values",
                    "output_status": "no_output",
                    "succeeded": False,
                    "output_files": [],
                    "status_message": "no data",
                    "log_path": "counter_values.log",
                },
            ],
        )
        assert result["export_status"][1]["status"] == "no_output"
        assert result["summary"]["diagnostics"]["export_status_counts"]["ok"] == 1
        assert result["summary"]["diagnostics"]["export_status_counts"]["no_output"] == 1

    @patch("cli_anything.unrealinsights.core.analyze.execute_export")
    def test_analyze_summary_runs_export_bundle(self, mock_export, tmp_path):
        from cli_anything.unrealinsights.core.analyze import analyze_summary

        def _fake_export(_exe, _trace, exporter, output_path, **_kwargs):
            if exporter == "timer-stats":
                Path(output_path).write_text("Timer Name,Total Time\nTick,1.0\n", encoding="utf-8")
            elif exporter == "counter-values":
                Path(output_path).write_text("Counter,Value\nFrameTime,16.0\n", encoding="utf-8")
            else:
                Path(output_path).write_text("Name\nx\n", encoding="utf-8")
            return {"exporter": exporter, "output_files": [output_path], "succeeded": True}

        mock_export.side_effect = _fake_export
        result = analyze_summary("C:/UE/UnrealInsights.exe", "C:/trace.utrace", str(tmp_path))
        assert result["succeeded"] is True
        assert mock_export.call_count == 5


class TestCLIHelp:
    def test_main_help(self):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Unreal Insights harness" in result.output

    def test_group_help(self):
        from cli_anything.unrealinsights.unrealinsights_cli import cli

        runner = CliRunner()
        for group in ("backend", "trace", "store", "capture", "live", "gui", "export", "batch", "analyze"):
            result = runner.invoke(cli, [group, "--help"])
            assert result.exit_code == 0, f"{group} help failed"
