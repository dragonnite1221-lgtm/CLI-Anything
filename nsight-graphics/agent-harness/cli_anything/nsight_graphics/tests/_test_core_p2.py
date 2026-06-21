# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestHelpParsing:
    def test_parse_unified_help_extracts_activities_and_options(self):
        result = backend.parse_unified_help(SAMPLE_HELP)
        assert result["activities"] == [
            "Graphics Capture",
            "OpenGL Frame Debugger",
            "Generate C++ Capture",
            "GPU Trace Profiler",
        ]
        assert result["platforms"] == ["Windows"]
        assert "--project" in result["general_options"]
        assert "--frame-index" in result["activity_options"]["Graphics Capture"]
        assert "--wait-frames" in result["activity_options"]["OpenGL Frame Debugger"]
        assert "--metric-set-id" in result["activity_options"]["GPU Trace Profiler"]


class TestCLIHelp:
    def test_root_help(self):
        from click.testing import CliRunner
        from cli_anything.nsight_graphics.nsight_graphics_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Nsight Graphics CLI" in result.output
        assert "--nsight-path" in result.output

    def test_nsight_path_is_forwarded_to_doctor(self):
        from click.testing import CliRunner
        from cli_anything.nsight_graphics.nsight_graphics_cli import cli

        runner = CliRunner()
        with patch("cli_anything.nsight_graphics.nsight_graphics_cli.doctor.get_installation_report") as doctor_mock:
            doctor_mock.return_value = {
                "ok": True,
                "compatibility_mode": "unified",
                "resolved_executable": "C:/Custom/ngfx.exe",
                "supported_activities": [],
                "warnings": [],
            }
            result = runner.invoke(cli, ["--json", "--nsight-path", "C:/Custom/NG", "doctor", "info"])

        assert result.exit_code == 0
        doctor_mock.assert_called_once_with(nsight_path="C:/Custom/NG")

    @pytest.mark.parametrize(
        ("args", "needle"),
        [
            (["doctor", "--help"], "info"),
            (["doctor", "--help"], "versions"),
            (["launch", "--help"], "detached"),
            (["frame", "--help"], "capture"),
            (["gpu-trace", "--help"], "capture"),
            (["gpu-trace", "--help"], "summarize"),
            (["replay", "--help"], "analyze"),
            (["cpp", "--help"], "capture"),
        ],
    )
    def test_group_help(self, args, needle):
        from click.testing import CliRunner
        from cli_anything.nsight_graphics.nsight_graphics_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        assert needle in result.output

    def test_replay_analyze_json_cli(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.nsight_graphics.nsight_graphics_cli import cli

        capture_file = tmp_path / "frame.ngfx-capture"
        capture_file.write_text("capture", encoding="utf-8")
        runner = CliRunner()
        with patch("cli_anything.nsight_graphics.nsight_graphics_cli.replay.analyze_capture") as analyze_mock:
            analyze_mock.return_value = {
                "ok": True,
                "capture_file": str(capture_file),
                "capture_type": "graphics_capture",
                "output_dir": str(tmp_path / "analysis"),
                "artifact_count": 1,
            }
            result = runner.invoke(
                cli,
                [
                    "--json",
                    "replay",
                    "analyze",
                    "--capture-file",
                    str(capture_file),
                    "--output-dir",
                    str(tmp_path / "analysis"),
                ],
            )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["ok"] is True
        analyze_mock.assert_called_once()
        assert analyze_mock.call_args.kwargs["metadata"] is False
        assert analyze_mock.call_args.kwargs["logs"] is False
        assert analyze_mock.call_args.kwargs["perf_report"] is False
