# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestExportCore:
    @pytest.mark.parametrize(
        ("exporter", "expected"),
        [
            ("threads", "TimingInsights.ExportThreads"),
            ("timers", "TimingInsights.ExportTimers"),
            ("timing-events", "TimingInsights.ExportTimingEvents"),
            ("timer-stats", "TimingInsights.ExportTimerStatistics"),
            ("timer-callees", "TimingInsights.ExportTimerCallees"),
            ("counters", "TimingInsights.ExportCounters"),
            ("counter-values", "TimingInsights.ExportCounterValues"),
        ],
    )
    def test_build_export_exec_command(self, exporter, expected, tmp_path):
        from cli_anything.unrealinsights.core.export import build_export_exec_command

        command = build_export_exec_command(
            exporter,
            str(tmp_path / f"{exporter}.csv"),
            columns="ThreadId,TimerId" if exporter in ("timing-events", "timer-stats", "counter-values") else None,
            threads="GameThread" if exporter in ("timing-events", "timer-stats", "timer-callees") else None,
            timers="*" if exporter in ("timing-events", "timer-stats", "timer-callees") else None,
            counter="*" if exporter == "counter-values" else None,
        )
        assert command.startswith(expected)
        if exporter == "counter-values":
            assert "-counter=*" in command
            assert '-counter="' not in command
        if exporter in ("timing-events", "timer-stats", "timer-callees"):
            assert "-threads=GameThread" in command
            assert "-timers=*" in command

    def test_build_rsp_exec_command(self, tmp_path):
        from cli_anything.unrealinsights.core.export import build_rsp_exec_command

        command = build_rsp_exec_command(str(tmp_path / "exports.rsp"))
        assert command.startswith("@=")

    @pytest.mark.skipif(os.name != "nt", reason="Windows quoting behavior")
    def test_normalize_rsp_line_modern_windows_avoids_nested_quotes(self, tmp_path):
        from cli_anything.unrealinsights.core.export import _normalize_rsp_line

        line, output = _normalize_rsp_line(
            f'TimingInsights.ExportThreads "{tmp_path / "threads.csv"}"',
            insights_version="5.5.4",
        )
        resolved = str((tmp_path / "threads.csv").resolve())
        assert f'"{resolved}"' not in line
        assert resolved in line
        assert output == resolved

    def test_build_export_exec_command_legacy_53_unquoted_filename(self, tmp_path):
        from cli_anything.unrealinsights.core.export import build_export_exec_command

        command = build_export_exec_command(
            "threads",
            str(tmp_path / "threads.csv"),
            insights_version="5.3.0",
        )
        assert '"{}"'.format(str((tmp_path / "threads.csv").resolve())) not in command
        assert str((tmp_path / "threads.csv").resolve()) in command

    @pytest.mark.skipif(os.name != "nt", reason="Windows quoting behavior")
    def test_build_export_exec_command_modern_windows_avoids_nested_quotes(self, tmp_path):
        from cli_anything.unrealinsights.core.export import build_export_exec_command

        command = build_export_exec_command(
            "threads",
            str(tmp_path / "threads.csv"),
            insights_version="5.5.4",
        )
        resolved = str((tmp_path / "threads.csv").resolve())
        assert f'"{resolved}"' not in command
        assert resolved in command

    @patch("cli_anything.unrealinsights.core.export.backend.parse_unreal_log")
    @patch("cli_anything.unrealinsights.core.export.backend.run_process")
    def test_execute_export_classifies_no_output(self, mock_run, mock_log, tmp_path):
        from cli_anything.unrealinsights.core.export import execute_export

        mock_run.return_value = {
            "command": "UnrealInsights.exe",
            "waited": True,
            "timed_out": False,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "pid": None,
        }
        mock_log.return_value = {
            "path": str(tmp_path / "export.log"),
            "exists": True,
            "warnings": [],
            "errors": [],
            "tail": [],
        }

        result = execute_export(
            "C:/UE/UnrealInsights.exe",
            "C:/trace.utrace",
            "counter-values",
            str(tmp_path / "counter_values.csv"),
        )
        assert result["output_status"] == "no_output"
        assert result["succeeded"] is False
        assert "without materializing" in result["status_message"]

    @patch("cli_anything.unrealinsights.core.export.backend.parse_unreal_log")
    @patch("cli_anything.unrealinsights.core.export.backend.run_process")
    def test_execute_export_classifies_exporter_error(self, mock_run, mock_log, tmp_path):
        from cli_anything.unrealinsights.core.export import execute_export

        mock_run.return_value = {
            "command": "UnrealInsights.exe",
            "waited": True,
            "timed_out": False,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "pid": None,
        }
        mock_log.return_value = {
            "path": str(tmp_path / "export.log"),
            "exists": True,
            "warnings": [],
            "errors": ["TimingInsights: Error: Export failed."],
            "tail": [],
        }

        result = execute_export(
            "C:/UE/UnrealInsights.exe",
            "C:/trace.utrace",
            "threads",
            str(tmp_path / "threads.csv"),
        )
        assert result["output_status"] == "exporter_error"
        assert result["status_message"] == "TimingInsights: Error: Export failed."

    def test_expected_outputs_from_rsp(self, tmp_path):
        from cli_anything.unrealinsights.core.export import expected_outputs_from_rsp

        rsp = tmp_path / "exports.rsp"
        rsp.write_text(
            "\n".join(
                [
                    "# comment",
                    f'TimingInsights.ExportThreads "{tmp_path / "threads.csv"}"',
                    f'TimingInsights.ExportTimers "{tmp_path / "timers.csv"}"',
                ]
            ),
            encoding="utf-8",
        )
        outputs = expected_outputs_from_rsp(str(rsp))
        assert str((tmp_path / "threads.csv").resolve()) in outputs
        assert str((tmp_path / "timers.csv").resolve()) in outputs

    def test_normalize_response_file_lines_unquotes_filename_without_spaces(self, tmp_path):
        from cli_anything.unrealinsights.core.export import normalize_response_file_lines

        output = tmp_path / "threads.csv"
        lines = [f'TimingInsights.ExportThreads "{output}"']
        normalized = normalize_response_file_lines(lines, insights_version="5.5.4")
        assert normalized[0] == f"TimingInsights.ExportThreads {output.resolve()}"

    def test_normalized_response_file_path_writes_temp_file(self, tmp_path):
        from cli_anything.unrealinsights.core.export import normalized_response_file_path

        output = tmp_path / "threads.csv"
        rsp = tmp_path / "exports.rsp"
        rsp.write_text(f'TimingInsights.ExportThreads "{output}"\n', encoding="utf-8")
        normalized_path = normalized_response_file_path(str(rsp), insights_version="5.5.4")
        assert normalized_path != str(rsp.resolve())
        assert f"TimingInsights.ExportThreads {output.resolve()}" in Path(normalized_path).read_text(encoding="utf-8")
        Path(normalized_path).unlink()

    def test_collect_materialized_outputs_placeholder(self, tmp_path):
        from cli_anything.unrealinsights.core.export import collect_materialized_outputs

        (tmp_path / "stats_GameThread.csv").write_text("ok", encoding="utf-8")
        outputs = collect_materialized_outputs(str(tmp_path / "stats_{region}.csv"))
        assert str((tmp_path / "stats_GameThread.csv").resolve()) in outputs
