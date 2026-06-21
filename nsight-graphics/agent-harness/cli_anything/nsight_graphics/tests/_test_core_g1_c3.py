# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin3:
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.probe_installation")
    def test_gpu_trace_capture_summary_requires_new_complete_export(self, probe_mock, build_mock, run_mock, tmp_path):
        old_export = tmp_path / "old"
        old_export.mkdir()
        (old_export / "FRAME.xls").write_text("GPU frame time\t16.0\n", encoding="utf-8")
        (old_export / "GPUTRACE_FRAME.xls").write_text("FE_B.TriageAC.fe__draw_count.sum\t1\n", encoding="utf-8")
        (old_export / "D3DPERF_EVENTS.xls").write_text("event_text\ttime_ms\nOldPass\t1.0\n", encoding="utf-8")

        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--activity", "GPU Trace Profiler"]
        run_mock.return_value = {
            "ok": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "command": "ngfx",
            "artifacts": [{"path": str(tmp_path / "capture.ngfx-gputrace"), "size": 1, "mtime_ns": 1}],
            "artifact_count": 1,
        }

        with pytest.raises(RuntimeError, match="complete newly exported table set"):
            gpu_trace.capture_trace(
                nsight_path=None,
                project=None,
                output_dir=str(tmp_path),
                hostname=None,
                platform_name=None,
                exe="C:/demo.exe",
                working_dir=None,
                args=(),
                envs=(),
                start_after_frames=1,
                start_after_submits=None,
                start_after_ms=None,
                start_after_hotkey=False,
                max_duration_ms=None,
                limit_to_frames=1,
                limit_to_submits=None,
                auto_export=False,
                architecture=None,
                metric_set_id=None,
                multi_pass_metrics=False,
                real_time_shader_profiler=False,
                summarize=True,
                summary_limit=5,
            )
