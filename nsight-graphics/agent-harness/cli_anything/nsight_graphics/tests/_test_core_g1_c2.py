# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin2:
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.probe_installation")
    def test_gpu_trace_capture_with_summary(self, probe_mock, build_mock, run_mock, tmp_path):
        base = tmp_path / "BASE"
        base.mkdir()
        (base / "FRAME.xls").write_text("GPU frame time\t16.0\n", encoding="utf-8")
        (base / "GPUTRACE_FRAME.xls").write_text(
            "FE_B.TriageAC.fe__draw_count.sum\t100\nFE_A.TriageAC.gr__dispatch_count.sum\t50\n",
            encoding="utf-8",
        )
        (base / "D3DPERF_EVENTS.xls").write_text(
            "event_text\ttime_ms\nFrame 1\t16.0\nScene\t10.0\n",
            encoding="utf-8",
        )

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
            "artifacts": [
                {"path": str(base / "FRAME.xls"), "size": 1, "mtime_ns": 1},
                {"path": str(base / "GPUTRACE_FRAME.xls"), "size": 1, "mtime_ns": 1},
                {"path": str(base / "D3DPERF_EVENTS.xls"), "size": 1, "mtime_ns": 1},
            ],
            "artifact_count": 3,
        }

        result = gpu_trace.capture_trace(
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

        assert result["auto_export"] is True
        assert result["summary"]["frame_time_ms"] == pytest.approx(16.0)
        assert result["summary"]["top_events"][0]["event"] == "Scene"
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.probe_installation")
    def test_gpu_trace_capture_summary_refuses_failed_capture(self, probe_mock, build_mock, run_mock, tmp_path):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--activity", "GPU Trace Profiler"]
        run_mock.return_value = {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": "capture failed",
            "command": "ngfx",
            "artifacts": [],
            "artifact_count": 0,
        }

        with pytest.raises(RuntimeError, match="refusing to summarize stale"):
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
