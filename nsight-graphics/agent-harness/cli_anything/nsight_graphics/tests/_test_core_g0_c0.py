# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCommandBuildersMixin0:
    def test_build_unified_command_formats_args_and_env(self):
        command = backend.build_unified_command(
            {"ngfx": "C:/Nsight/ngfx.exe"},
            activity="Frame Debugger",
            project="demo.ngfx-proj",
            output_dir="D:/out",
            hostname="localhost",
            platform_name="Windows",
            exe="C:/demo.exe",
            working_dir="C:/demo",
            args=["--flag", "value with spaces"],
            envs=["A=1", "B=two"],
            launch_detached=True,
            extra_args=["--wait-frames", "10"],
        )
        assert command[0] == "C:/Nsight/ngfx.exe"
        assert "--launch-detached" in command
        assert "--args" in command
        assert "--env" in command
        assert "value with spaces" in command[command.index("--args") + 1]
        assert command[command.index("--env") + 1].endswith(";")
    def test_build_split_capture_command_maps_wait_seconds(self):
        command = backend.build_split_capture_command(
            {"ngfx_capture": "C:/Nsight/ngfx-capture.exe"},
            exe="C:/demo.exe",
            wait_seconds=3,
            wait_frames=None,
            wait_hotkey=False,
        )
        assert command[0] == "C:/Nsight/ngfx-capture.exe"
        assert "--capture-countdown-timer" in command
        assert command[command.index("--capture-countdown-timer") + 1] == "3000"
    def test_build_replay_command_uses_capture_file_as_positional(self):
        command = backend.build_replay_command(
            {"ngfx_replay": "C:/Nsight/ngfx-replay.exe"},
            capture_file="D:/captures/frame.ngfx-capture",
            extra_args=["--metadata"],
        )
        assert command == [
            "C:/Nsight/ngfx-replay.exe",
            "--metadata",
            "D:/captures/frame.ngfx-capture",
        ]
    def test_diff_snapshots_reports_new_nonempty_files(self, tmp_path):
        before = backend.snapshot_files([str(tmp_path)])
        artifact = tmp_path / "capture.ngfx-capture"
        artifact.write_text("data", encoding="utf-8")
        after = backend.snapshot_files([str(tmp_path)])
        diff = backend.diff_snapshots(before, after)
        assert len(diff) == 1
        assert diff[0]["path"].endswith("capture.ngfx-capture")
        assert diff[0]["size"] > 0
    def test_gpu_trace_summary_from_export_dir(self, tmp_path):
        base = tmp_path / "BASE"
        base.mkdir()
        (base / "FRAME.xls").write_text("GPU frame time\t31.0446\n", encoding="utf-8")
        (base / "GPUTRACE_FRAME.xls").write_text(
            "\n".join(
                [
                    "FE_B.TriageAC.fe__draw_count.sum\t309",
                    "FE_A.TriageAC.gr__dispatch_count.sum\t2561",
                    "FE_B.TriageAC.gr__cycles_active.avg.pct_of_peak_sustained_elapsed\t98.1079",
                    "FE_A.TriageAC.gr__compute_cycles_active_queue_sync.avg.pct_of_peak_sustained_elapsed\t84.24",
                    "TriageAC.sm__throughput.avg.pct_of_peak_sustained_elapsed\t23.6331",
                    "LTS.TriageAC.lts__throughput.avg.pct_of_peak_sustained_elapsed\t32.0437",
                    "FBSP.TriageAC.dramc__throughput.avg.pct_of_peak_sustained_elapsed\t19.5897",
                    "PCI.TriageAC.pcie__throughput.avg.pct_of_peak_sustained_elapsed\t12.0",
                    "SM_A.TriageAC.sm__inst_executed_realtime.sum\t123456",
                ]
            ),
            encoding="utf-8",
        )
        (base / "D3DPERF_EVENTS.xls").write_text(
            "event_text\ttime_ms\n"
            "Frame 1221\t31.0431\n"
            "Scene\t29.9644\n"
            "        DirectLighting\t15.3828\n"
            "        ReSTIRDI\t14.0627\n",
            encoding="utf-8",
        )
        (base / "GPUTRACE_REGIMES.xls").write_text(
            "flattened_event_name\tTriageAC.sm__throughput.avg.pct_of_peak_sustained_elapsed\n"
            "Scene\t23.6331\n",
            encoding="utf-8",
        )

        summary = gpu_trace.summarize_export_dir(str(tmp_path), top_n=3)
        assert summary["frame_time_ms"] == pytest.approx(31.0446)
        assert summary["fps_estimate"] == pytest.approx(1000.0 / 31.0446)
        assert summary["metrics"]["draw_count"] == 309
        assert summary["metrics"]["dispatch_count"] == 2561
        assert summary["tables"]["trace_frame"]["metric_count"] == 9
        assert summary["tables"]["events"]["row_count"] == 4
        assert summary["tables"]["regimes"]["row_count"] == 1
        assert summary["metric_inventory"]["metric_count"] == 9
        assert summary["metric_inventory"]["top_pct_of_peak_metrics"][0]["metric"].endswith(
            "gr__cycles_active.avg.pct_of_peak_sustained_elapsed"
        )
        assert summary["top_events"][0]["event"] == "Scene"
        assert summary["top_events"][1]["event"] == "DirectLighting"
        assert summary["analysis"]["workload"]["classification"] == "compute_heavy"
        assert summary["analysis"]["throughput"]["dominant_unit"]["name"] == "graphics_engine"
        assert summary["analysis"]["event_summary"]["event_count"] == 3
        assert any(item["id"] == "frame_budget_60fps" for item in summary["analysis"]["bottlenecks"])
        assert summary["highlights"]
