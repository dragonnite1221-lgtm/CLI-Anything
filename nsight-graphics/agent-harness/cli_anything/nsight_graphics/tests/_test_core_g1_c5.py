# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin5:
    @patch("cli_anything.nsight_graphics.core.replay.backend.run_command")
    @patch("cli_anything.nsight_graphics.core.replay.backend.probe_installation")
    def test_replay_analyze_defaults_to_metadata_logs_and_perf(self, probe_mock, run_mock, tmp_path):
        capture_file = tmp_path / "trace.ngfx-gputrace"
        capture_file.write_text("trace", encoding="utf-8")
        probe_mock.return_value = {
            "version": "2026.1.0",
            "tool_mode": "unified+split",
            "compatibility_mode": "unified+split",
            "binaries": {"ngfx_replay": "C:/Nsight/ngfx-replay.exe"},
        }

        def fake_run(command, timeout=120, cwd=None):
            if "--perf-report-dir" in command:
                perf_dir = Path(command[command.index("--perf-report-dir") + 1])
                perf_dir.mkdir(parents=True, exist_ok=True)
                (perf_dir / "report.txt").write_text("perf", encoding="utf-8")
                stdout = ""
            else:
                stdout = "output"
            return {
                "ok": True,
                "returncode": 0,
                "stdout": stdout,
                "stderr": "",
                "command": " ".join(command),
            }

        run_mock.side_effect = fake_run

        result = replay.analyze_capture(
            nsight_path=None,
            capture_file=str(capture_file),
            output_dir=str(tmp_path / "analysis"),
            metadata=False,
            logs=False,
            screenshot=False,
            perf_report=False,
        )

        assert result["capture_type"] == "gpu_trace"
        assert result["requested_outputs"] == {
            "metadata": True,
            "logs": True,
            "screenshot": False,
            "perf_report": True,
        }
        assert any(".ngfx-gputrace inputs may not produce metadata" in warning for warning in result["analysis"]["warnings"])
    @patch("cli_anything.nsight_graphics.core.replay.backend.run_command")
    @patch("cli_anything.nsight_graphics.core.replay.backend.probe_installation")
    def test_replay_analyze_filters_no_error_log_marker(self, probe_mock, run_mock, tmp_path):
        capture_file = tmp_path / "frame.ngfx-capture"
        capture_file.write_text("capture", encoding="utf-8")
        probe_mock.return_value = {
            "version": "2026.1.0",
            "tool_mode": "unified+split",
            "compatibility_mode": "unified+split",
            "binaries": {"ngfx_replay": "C:/Nsight/ngfx-replay.exe"},
        }

        def fake_run(command, timeout=120, cwd=None):
            stdout = "No log messages found with severity >= 2\n" if "--metadata-logs-errors" in command else ""
            return {
                "ok": True,
                "returncode": 0,
                "stdout": stdout,
                "stderr": "",
                "command": " ".join(command),
            }

        run_mock.side_effect = fake_run

        result = replay.analyze_capture(
            nsight_path=None,
            capture_file=str(capture_file),
            output_dir=str(tmp_path / "analysis"),
            metadata=False,
            logs=True,
            screenshot=False,
            perf_report=False,
        )

        assert result["ok"] is True
        assert result["logs"]["status"] == "no_errors"
        assert result["logs"]["error_line_count"] == 0
        assert result["logs"]["error_summary"] == []
        assert result["logs"]["raw_error_summary"] == ["No log messages found with severity >= 2"]
        assert any("no severity >= 2 errors" in item for item in result["analysis"]["highlights"])
