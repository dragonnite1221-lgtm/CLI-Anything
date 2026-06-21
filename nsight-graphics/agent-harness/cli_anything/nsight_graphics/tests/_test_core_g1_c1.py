# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin1:
    @patch("cli_anything.nsight_graphics.core.gpu_trace.backend.probe_installation")
    def test_gpu_trace_requires_arch_for_metric_set(self, probe_mock):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
        }
        with pytest.raises(ValueError, match="requires --architecture"):
            gpu_trace.capture_trace(
                nsight_path=None,
                project=None,
                output_dir=None,
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
                metric_set_id="1",
                multi_pass_metrics=False,
                real_time_shader_profiler=False,
            )
    @patch("cli_anything.nsight_graphics.core.launch.backend.run_command")
    @patch("cli_anything.nsight_graphics.core.launch.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.launch.backend.probe_installation")
    def test_launch_attach_returns_unified_result(self, probe_mock, build_mock, run_mock):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--attach-pid", "123"]
        run_mock.return_value = {
            "ok": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "command": "ngfx",
        }

        result = launch.attach(
            nsight_path=None,
            activity="Frame Debugger",
            pid=123,
            project=None,
            output_dir=None,
            hostname=None,
            platform_name=None,
        )
        assert result["tool_mode"] == "unified"
        assert result["pid"] == 123
    @patch("cli_anything.nsight_graphics.core.cpp_capture.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.cpp_capture.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.cpp_capture.backend.probe_installation")
    def test_cpp_capture_sets_activity(self, probe_mock, build_mock, run_mock, tmp_path):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--activity", "Generate C++ Capture"]
        run_mock.return_value = {
            "ok": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "command": "ngfx",
            "artifacts": [],
        }
        result = cpp_capture.capture_cpp(
            nsight_path=None,
            project=None,
            output_dir=str(tmp_path / "out"),
            hostname=None,
            platform_name=None,
            exe="C:/demo.exe",
            working_dir=None,
            args=(),
            envs=(),
            wait_seconds=5,
            wait_hotkey=False,
        )
        assert result["activity"] == "Generate C++ Capture"
        assert result["tool_mode"] == "unified"
