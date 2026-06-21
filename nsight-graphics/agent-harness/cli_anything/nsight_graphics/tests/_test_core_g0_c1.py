# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestCommandBuildersMixin1:
    def test_gpu_trace_summary_reports_empty_event_and_regime_tables(self, tmp_path):
        base = tmp_path / "BASE"
        base.mkdir()
        (base / "FRAME.xls").write_text("GPU frame time\t1.5\n", encoding="utf-8")
        (base / "GPUTRACE_FRAME.xls").write_text(
            "\n".join(
                [
                    "FE_B.TriageAC.fe__draw_count.sum\t38",
                    "FE_A.TriageAC.gr__dispatch_count.sum\t0",
                    "FE_B.TriageAC.gr__cycles_active.avg.pct_of_peak_sustained_elapsed\t12.0",
                    "TriageAC.sm__throughput.avg.pct_of_peak_sustained_elapsed\t3.0",
                    "SM_B.TriageAC.l1tex__t_sector_hit_rate.pct\t96.0",
                ]
            ),
            encoding="utf-8",
        )
        (base / "D3DPERF_EVENTS.xls").write_text("event_text\ttime_ms\n", encoding="utf-8")
        (base / "GPUTRACE_REGIMES.xls").write_text(
            "flattened_event_name\tFE_B.TriageAC.gr__cycles_active.avg.pct_of_peak_sustained_elapsed\n",
            encoding="utf-8",
        )

        summary = gpu_trace.summarize_export_dir(str(tmp_path), top_n=2)

        assert summary["tables"]["events"]["row_count"] == 0
        assert summary["tables"]["regimes"]["present"] is True
        assert summary["tables"]["regimes"]["row_count"] == 0
        assert summary["analysis"]["event_summary"]["event_count"] == 0
        assert summary["analysis"]["frame_budget"]["bucket"] == "within_60fps_budget"
        assert summary["analysis"]["workload"]["classification"] == "mixed"
        assert any("D3DPERF_EVENTS.xls contains no timed GPU event rows" in warning for warning in summary["analysis"]["warnings"])
        assert any("GPUTRACE_REGIMES.xls contains headers" in warning for warning in summary["analysis"]["warnings"])
    def test_gpu_trace_summary_prefers_newest_complete_export_dir(self, tmp_path):
        old_export = tmp_path / "A_old_export"
        new_export = tmp_path / "B_new_export"
        old_export.mkdir()
        new_export.mkdir()

        old_files = {
            "frame": old_export / "FRAME.xls",
            "trace": old_export / "GPUTRACE_FRAME.xls",
            "events": old_export / "D3DPERF_EVENTS.xls",
        }
        old_files["frame"].write_text("GPU frame time\t40.0\n", encoding="utf-8")
        old_files["trace"].write_text(
            "FE_B.TriageAC.fe__draw_count.sum\t10\n",
            encoding="utf-8",
        )
        old_files["events"].write_text(
            "event_text\ttime_ms\nFrame 1\t40.0\nOldPass\t30.0\n",
            encoding="utf-8",
        )

        new_files = {
            "frame": new_export / "FRAME.xls",
            "trace": new_export / "GPUTRACE_FRAME.xls",
            "events": new_export / "D3DPERF_EVENTS.xls",
        }
        new_files["frame"].write_text("GPU frame time\t12.5\n", encoding="utf-8")
        new_files["trace"].write_text(
            "FE_B.TriageAC.fe__draw_count.sum\t123\n",
            encoding="utf-8",
        )
        new_files["events"].write_text(
            "event_text\ttime_ms\nFrame 2\t12.5\nNewPass\t8.5\n",
            encoding="utf-8",
        )

        for path in old_files.values():
            os.utime(path, ns=(1_000_000_000, 1_000_000_000))
        for path in new_files.values():
            os.utime(path, ns=(2_000_000_000, 2_000_000_000))

        summary = gpu_trace.summarize_export_dir(str(tmp_path), top_n=3)

        assert summary["output_dir"] == str(new_export.resolve())
        assert summary["search_root"] == str(tmp_path.resolve())
        assert summary["frame_time_ms"] == pytest.approx(12.5)
        assert summary["metrics"]["draw_count"] == 123
        assert summary["top_events"][0]["event"] == "NewPass"
        assert Path(summary["files"]["frame"]).parent == new_export.resolve()
        assert Path(summary["files"]["trace_frame"]).parent == new_export.resolve()
        assert Path(summary["files"]["events"]).parent == new_export.resolve()
