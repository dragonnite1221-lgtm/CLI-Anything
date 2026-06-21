# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin6:
    @patch("cli_anything.nsight_graphics.core.replay.backend.run_command")
    @patch("cli_anything.nsight_graphics.core.replay.backend.probe_installation")
    def test_replay_analyze_reports_gputrace_replay_incompatibility(self, probe_mock, run_mock, tmp_path):
        capture_file = tmp_path / "trace.ngfx-gputrace"
        capture_file.write_text("trace", encoding="utf-8")
        probe_mock.return_value = {
            "version": "2026.1.0",
            "tool_mode": "unified+split",
            "compatibility_mode": "unified+split",
            "binaries": {"ngfx_replay": "C:/Nsight/ngfx-replay.exe"},
        }

        def fake_run(command, timeout=120, cwd=None):
            is_log_command = "--metadata-logs" in command or "--metadata-logs-errors" in command
            return {
                "ok": not is_log_command,
                "returncode": 1 if is_log_command else 0,
                "stdout": "ERROR: Invalid file header (trace.ngfx-gputrace)\n" if is_log_command else "",
                "stderr": "",
                "command": " ".join(command),
            }

        run_mock.side_effect = fake_run

        result = replay.analyze_capture(
            nsight_path=None,
            capture_file=str(capture_file),
            output_dir=str(tmp_path / "analysis"),
            metadata=True,
            logs=True,
            screenshot=False,
            perf_report=False,
        )

        assert result["ok"] is False
        assert result["metadata"]["present"] == {"summary": False, "functions": False, "objects": False}
        assert result["logs"]["error_line_count"] == 1
        assert "Invalid file header" in result["logs"]["error_summary"][0]
        assert any(".ngfx-gputrace inputs may not produce metadata" in warning for warning in result["analysis"]["warnings"])
        assert any("Replay command failures" in warning for warning in result["analysis"]["warnings"])
    @patch("cli_anything.nsight_graphics.core.replay.backend.probe_installation")
    def test_replay_analyze_requires_ngfx_replay(self, probe_mock, tmp_path):
        capture_file = tmp_path / "frame.ngfx-capture"
        capture_file.write_text("capture", encoding="utf-8")
        probe_mock.return_value = {
            "binaries": {"ngfx_replay": None},
        }
        with pytest.raises(RuntimeError, match="ngfx-replay.exe is required"):
            replay.analyze_capture(
                nsight_path=None,
                capture_file=str(capture_file),
                output_dir=str(tmp_path / "analysis"),
                metadata=True,
                logs=False,
                screenshot=False,
                perf_report=False,
            )
    def test_replay_analyze_rejects_unknown_capture_extension(self, tmp_path):
        capture_file = tmp_path / "frame.rdc"
        capture_file.write_text("capture", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported Nsight capture file extension"):
            replay.analyze_capture(
                nsight_path=None,
                capture_file=str(capture_file),
                output_dir=str(tmp_path / "analysis"),
                metadata=True,
                logs=False,
                screenshot=False,
                perf_report=False,
            )
