# ruff: noqa: F403, F405, E501
from .gpu_trace_base import *  # noqa: F403

# fmt: off
from .gpu_trace_p1 import _find_export_dir, _read_event_rows, _read_kv_file, _read_table_rows, _safe_float, _safe_int  # noqa: E402,E501
from .gpu_trace_p2 import _event_depth, _metric_inventory, _pick_metric, _table_inventory  # noqa: E402,E501
from .gpu_trace_p3 import _build_trace_analysis, _make_highlights  # noqa: E402,E501
# fmt: on


def summarize_export_dir(
    output_dir: str,
    top_n: int = 10,
    *,
    artifact_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Summarize exported GPU Trace tables from an output directory."""
    output_root = str(Path(output_dir).resolve())
    export_dir, files = _find_export_dir(output_root, artifact_paths=artifact_paths)
    frame_path = files["frame"]
    trace_frame_path = files["trace_frame"]
    events_path = files["events"]
    regimes_path = files["regimes"]

    frame_data = _read_kv_file(frame_path)
    trace_metrics = _read_kv_file(trace_frame_path)
    event_rows = _read_event_rows(events_path)
    regime_columns, regime_rows = _read_table_rows(regimes_path)

    frame_time_ms = _safe_float(frame_data.get("GPU frame time"))
    fps_estimate = (
        (1000.0 / frame_time_ms) if frame_time_ms and frame_time_ms > 0 else None
    )

    summary_metrics: dict[str, float | int | None] = {}
    for name, needle in SUMMARY_METRICS.items():
        value = _pick_metric(trace_metrics, needle)
        if name in {"draw_count", "dispatch_count"}:
            summary_metrics[name] = _safe_int(value)
        else:
            summary_metrics[name] = value

    ranked_events: list[dict[str, Any]] = []
    for row in event_rows:
        event_name = row["event_text"]
        if event_name.startswith("Frame "):
            continue
        time_ms = _safe_float(row["time_ms"])
        if time_ms is None or time_ms <= 0:
            continue
        ranked_events.append(
            {
                "event": event_name.strip(),
                "time_ms": time_ms,
                "depth": _event_depth(event_name),
            }
        )

    ranked_events.sort(key=lambda item: item["time_ms"], reverse=True)
    top_events = ranked_events[:top_n]
    top_level_events = [item for item in ranked_events if item["depth"] == 0][:top_n]
    tables = _table_inventory(
        files=files,
        frame_data=frame_data,
        trace_metrics=trace_metrics,
        event_rows=event_rows,
        regime_columns=regime_columns,
        regime_rows=regime_rows,
    )
    analysis = _build_trace_analysis(
        frame_time_ms=frame_time_ms,
        fps_estimate=fps_estimate,
        metrics=summary_metrics,
        ranked_events=ranked_events,
        table_inventory=tables,
    )
    highlights = (
        _make_highlights(frame_time_ms, summary_metrics, top_events)
        + analysis["highlights"]
    )

    return {
        "output_dir": export_dir,
        "search_root": output_root,
        "files": files,
        "tables": tables,
        "frame_time_ms": frame_time_ms,
        "fps_estimate": fps_estimate,
        "metrics": summary_metrics,
        "metric_inventory": _metric_inventory(trace_metrics, top_n),
        "top_events": top_events,
        "top_level_events": top_level_events,
        "highlights": highlights,
        "analysis": analysis,
    }
