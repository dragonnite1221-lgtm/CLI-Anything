# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin0:
    @patch("cli_anything.nsight_graphics.core.frame.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.frame.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.frame.backend.probe_installation")
    def test_frame_capture_uses_unified_ngfx(self, probe_mock, build_mock, run_mock, tmp_path):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
            "supported_activities": ["Graphics Capture", "OpenGL Frame Debugger"],
            "activity_options": {
                "Graphics Capture": ["--frame-count", "--frame-index", "--elapsed-time", "--hotkey-capture"],
                "OpenGL Frame Debugger": ["--wait-frames", "--wait-seconds", "--wait-hotkey"],
            },
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--activity", "Graphics Capture"]
        run_mock.return_value = {
            "ok": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "command": "ngfx",
            "artifacts": [{"path": "D:/out/capture.ngfx-capture", "size": 10, "mtime_ns": 1}],
        }

        result = frame.capture_frame(
            nsight_path=None,
            project=None,
            output_dir=str(tmp_path / "out"),
            hostname=None,
            platform_name=None,
            exe="C:/demo.exe",
            working_dir=None,
            args=(),
            envs=(),
            activity=None,
            wait_seconds=None,
            wait_frames=10,
            wait_hotkey=False,
            export_frame_perf_metrics=False,
            export_range_perf_metrics=False,
        )

        assert build_mock.called
        assert build_mock.call_args.kwargs["activity"] == "Graphics Capture"
        assert "--frame-index" in build_mock.call_args.kwargs["extra_args"]
        assert result["tool_mode"] == "unified"
        assert result["activity"] == "Graphics Capture"
        assert result["artifacts"]
    @patch("cli_anything.nsight_graphics.core.frame.backend.run_with_artifacts")
    @patch("cli_anything.nsight_graphics.core.frame.backend.build_unified_command")
    @patch("cli_anything.nsight_graphics.core.frame.backend.probe_installation")
    def test_frame_capture_allows_explicit_opengl_frame_debugger(self, probe_mock, build_mock, run_mock, tmp_path):
        probe_mock.return_value = {
            "binaries": {"ngfx": "C:/Nsight/ngfx.exe", "ngfx_capture": None, "ngfx_replay": None},
            "supported_activities": ["Graphics Capture", "OpenGL Frame Debugger"],
            "activity_options": {
                "Graphics Capture": ["--frame-count", "--frame-index", "--elapsed-time", "--hotkey-capture"],
                "OpenGL Frame Debugger": ["--wait-frames", "--wait-seconds", "--wait-hotkey"],
            },
        }
        build_mock.return_value = ["C:/Nsight/ngfx.exe", "--activity", "OpenGL Frame Debugger"]
        run_mock.return_value = {
            "ok": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "command": "ngfx",
            "artifacts": [],
        }

        result = frame.capture_frame(
            nsight_path=None,
            project=None,
            output_dir=str(tmp_path / "out"),
            hostname=None,
            platform_name=None,
            exe="C:/demo.exe",
            working_dir=None,
            args=(),
            envs=(),
            activity="OpenGL Frame Debugger",
            wait_seconds=None,
            wait_frames=10,
            wait_hotkey=False,
            export_frame_perf_metrics=False,
            export_range_perf_metrics=False,
        )

        assert build_mock.call_args.kwargs["activity"] == "OpenGL Frame Debugger"
        assert "--wait-frames" in build_mock.call_args.kwargs["extra_args"]
        assert result["activity"] == "OpenGL Frame Debugger"
    @patch("cli_anything.nsight_graphics.core.frame.backend.probe_installation")
    def test_frame_capture_split_mode_rejects_perf_exports(self, probe_mock):
        probe_mock.return_value = {
            "binaries": {"ngfx": None, "ngfx_capture": "C:/Nsight/ngfx-capture.exe", "ngfx_replay": None},
        }
        with pytest.raises(RuntimeError, match="Frame performance export flags"):
            frame.capture_frame(
                nsight_path=None,
                project=None,
                output_dir=None,
                hostname=None,
                platform_name=None,
                exe="C:/demo.exe",
                working_dir=None,
                args=(),
                envs=(),
                activity=None,
                wait_seconds=None,
                wait_frames=1,
                wait_hotkey=False,
                export_frame_perf_metrics=True,
                export_range_perf_metrics=False,
            )
