# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCoreModulesMixin4:
    @patch("cli_anything.nsight_graphics.core.replay.backend.run_command")
    @patch("cli_anything.nsight_graphics.core.replay.backend.probe_installation")
    def test_replay_analyze_exports_requested_metadata_logs_screenshot_and_perf(self, probe_mock, run_mock, tmp_path):
        capture_file = tmp_path / "frame.ngfx-capture"
        capture_file.write_text("capture", encoding="utf-8")

        probe_mock.return_value = {
            "version": "2026.1.0",
            "tool_mode": "unified+split",
            "compatibility_mode": "unified+split",
            "binaries": {"ngfx_replay": "C:/Nsight/ngfx-replay.exe"},
        }

        def fake_run(command, timeout=120, cwd=None):
            if "--metadata-screenshot" in command:
                screenshot_path = Path(command[command.index("--metadata-screenshot") + 1])
                screenshot_path.write_bytes(b"png")
                stdout = ""
            elif "--perf-report-dir" in command:
                perf_dir = Path(command[command.index("--perf-report-dir") + 1])
                perf_dir.mkdir(parents=True, exist_ok=True)
                (perf_dir / "report.txt").write_text("perf", encoding="utf-8")
                stdout = ""
            elif "--metadata-functions" in command:
                stdout = json.dumps(
                    [
                        {"function_name": "vkQueueSubmit", "sequence_id": 1, "thread_index": 0},
                        {"function_name": "vkQueueSubmit", "sequence_id": 2, "thread_index": 0},
                        {"function_name": "vkCreateImage", "sequence_id": 3, "thread_index": 1},
                    ]
                )
            elif "--metadata-objects" in command:
                stdout = json.dumps(
                    [
                        {"api": "Vulkan", "object_name": "Device_1", "type_name": "Device", "uid": 1},
                        {"api": "Vulkan", "object_name": "Image_2", "type_name": "Image", "uid": 2},
                        {"api": "Vulkan", "object_name": "Image_3", "type_name": "Image", "uid": 3},
                    ]
                )
            elif "--metadata-logs-errors" in command:
                stdout = "Captured error A\nCaptured error B\n"
            elif "--metadata-logs" in command:
                stdout = "Captured info A\n"
            elif "--metadata" in command:
                stdout = json.dumps(
                    {
                        "nsight_version": "2026.1.0",
                        "captured_frame": "2",
                        "primary_api": "Vulkan",
                        "primary_gpu": "NVIDIA GeForce RTX 4070 Ti",
                        "driver_vendor": "NVIDIA",
                        "driver_version": "591.74",
                        "graphics_apis": {"Vulkan": ["general"]},
                    }
                )
            else:
                stdout = f"{command[1]} output"
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
            metadata=True,
            logs=True,
            screenshot=True,
            perf_report=True,
        )

        assert result["ok"] is True
        assert result["capture_type"] == "graphics_capture"
        assert result["metadata"]["present"]["functions"] is True
        assert result["metadata"]["present"]["objects"] is True
        assert result["metadata"]["summary"]["primary_api"] == "Vulkan"
        assert result["metadata"]["summary"]["primary_gpu"] == "NVIDIA GeForce RTX 4070 Ti"
        assert result["metadata"]["functions"]["total"] == 3
        assert result["metadata"]["functions"]["top_functions"][0] == {"name": "vkQueueSubmit", "count": 2}
        assert result["metadata"]["objects"]["total"] == 3
        assert result["metadata"]["objects"]["top_types"][0] == {"name": "Image", "count": 2}
        assert result["logs"]["error_line_count"] == 2
        assert result["logs"]["error_summary"] == ["Captured error A", "Captured error B"]
        assert result["screenshot"]["present"] is True
        assert result["perf_report"]["present"] is True
        assert result["analysis"]["summary"]["object_count"] == 3
        assert result["analysis"]["summary"]["function_event_count"] == 3
        assert result["analysis"]["summary"]["log_error_count"] == 2
        assert any("Captured log errors" in warning for warning in result["analysis"]["warnings"])
        commands = [item["command"] for item in result["command_results"]]
        assert any("--metadata-objects" in command for command in commands)
        assert any("--metadata-logs" in command for command in commands)
        assert any("--metadata-screenshot" in command for command in commands)
        assert any("--perf-report-dir" in command for command in commands)
