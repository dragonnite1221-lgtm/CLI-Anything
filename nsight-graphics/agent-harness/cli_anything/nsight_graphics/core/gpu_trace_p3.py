# ruff: noqa: F403, F405, E501
from .gpu_trace_base import *  # noqa: F403

# fmt: off
from .gpu_trace_p2 import _frame_budget, _workload_classification  # noqa: E402,E501
# fmt: on


def _throughput_units(metrics: dict[str, float | int | None]) -> list[dict[str, Any]]:
    """Rank selected throughput metrics by utilization."""
    units = [
        ("graphics_engine", "graphics_engine_active_pct"),
        ("shader_sm", "sm_throughput_pct"),
        ("l1_texture", "l1tex_throughput_pct"),
        ("l2_cache", "l2_throughput_pct"),
        ("dram", "dram_throughput_pct"),
        ("pcie", "pcie_throughput_pct"),
        ("sync_compute", "compute_queue_sync_active_pct"),
        ("async_compute", "compute_queue_async_active_pct"),
    ]
    ranked = [
        {"name": name, "metric": metric_name, "pct": value}
        for name, metric_name in units
        if isinstance((value := metrics.get(metric_name)), float)
    ]
    ranked.sort(key=lambda item: item["pct"], reverse=True)
    return ranked


def _build_trace_analysis(
    *,
    frame_time_ms: float | None,
    fps_estimate: float | None,
    metrics: dict[str, float | int | None],
    ranked_events: list[dict[str, Any]],
    table_inventory: dict[str, Any],
) -> dict[str, Any]:
    """Build higher-level GPU Trace diagnostics from exported tables."""
    budget = _frame_budget(frame_time_ms, fps_estimate)
    workload = _workload_classification(metrics)
    throughput_units = _throughput_units(metrics)
    dominant_unit = throughput_units[0] if throughput_units else None
    event_depths = [item["depth"] for item in ranked_events]

    bottlenecks: list[dict[str, Any]] = []
    recommendations: list[str] = []
    warnings: list[str] = []
    highlights: list[str] = []

    if budget["bucket"] == "over_30fps_budget":
        bottlenecks.append(
            {
                "id": "frame_budget_30fps",
                "severity": "high",
                "value": frame_time_ms,
                "message": "GPU frame time exceeds a 30 FPS budget.",
            }
        )
        recommendations.append(
            "Start from the longest GPU events and reduce work on the critical frame path."
        )
    elif budget["bucket"] == "over_60fps_budget":
        bottlenecks.append(
            {
                "id": "frame_budget_60fps",
                "severity": "medium",
                "value": frame_time_ms,
                "message": "GPU frame time exceeds a 60 FPS budget.",
            }
        )

    for item in throughput_units:
        pct = item["pct"]
        if pct >= 80.0:
            severity = "high"
        elif pct >= 60.0:
            severity = "medium"
        else:
            continue
        bottlenecks.append(
            {
                "id": f"high_{item['name']}_throughput",
                "severity": severity,
                "value": pct,
                "message": f"{item['name']} utilization is {pct:.1f}% of peak sustained elapsed.",
            }
        )

    if workload["classification"] == "compute_heavy":
        recommendations.append(
            "Dispatch count dominates draw count; inspect compute workloads and synchronization."
        )
    if any(item["name"] == "dram" and item["pct"] >= 60.0 for item in throughput_units):
        recommendations.append(
            "DRAM throughput is high; inspect bandwidth, render target size, and cache locality."
        )
    if any(item["name"] == "pcie" and item["pct"] >= 60.0 for item in throughput_units):
        recommendations.append(
            "PCIe throughput is high; inspect uploads, readbacks, and host-visible buffer traffic."
        )
    if any(
        item["name"] == "shader_sm" and item["pct"] >= 60.0 for item in throughput_units
    ):
        recommendations.append(
            "SM throughput is high; inspect expensive shaders and dispatch/draw ranges."
        )
    if not ranked_events:
        warnings.append(
            "D3DPERF_EVENTS.xls contains no timed GPU event rows; add markers/NVTX ranges for pass-level attribution."
        )
    if (
        table_inventory["regimes"]["present"]
        and table_inventory["regimes"]["row_count"] == 0
    ):
        warnings.append("GPUTRACE_REGIMES.xls contains headers but no per-regime rows.")

    if dominant_unit:
        highlights.append(
            f"Dominant throughput unit: {dominant_unit['name']} at {dominant_unit['pct']:.3f}%."
        )
    if workload["classification"] != "unknown":
        highlights.append(
            f"Workload classification: {workload['classification']} "
            f"({workload['draw_count']} draws, {workload['dispatch_count']} dispatches)."
        )

    return {
        "frame_budget": budget,
        "workload": workload,
        "throughput": {
            "dominant_unit": dominant_unit,
            "top_units": throughput_units,
        },
        "event_summary": {
            "event_count": len(ranked_events),
            "top_level_event_count": sum(
                1 for item in ranked_events if item["depth"] == 0
            ),
            "max_depth": max(event_depths) if event_depths else 0,
        },
        "bottlenecks": bottlenecks,
        "recommendations": recommendations,
        "warnings": warnings,
        "highlights": highlights,
    }


def _make_highlights(
    frame_time_ms: float | None,
    metrics: dict[str, float | int | None],
    top_events: list[dict[str, Any]],
) -> list[str]:
    """Generate short heuristic findings."""
    highlights: list[str] = []

    if frame_time_ms is not None:
        if frame_time_ms > 33.3:
            highlights.append("GPU frame is slower than 30 FPS budget.")
        elif frame_time_ms > 16.7:
            highlights.append("GPU frame exceeds 60 FPS budget.")

    draw_count = metrics.get("draw_count")
    dispatch_count = metrics.get("dispatch_count")
    if isinstance(draw_count, int) and isinstance(dispatch_count, int):
        if dispatch_count > max(draw_count * 2, 500):
            highlights.append("Frame is compute-heavy relative to draw count.")

    compute_sync = metrics.get("compute_queue_sync_active_pct")
    if isinstance(compute_sync, float) and compute_sync > 50.0:
        highlights.append("Synchronous compute queue activity is high.")

    dram_pct = metrics.get("dram_throughput_pct")
    if isinstance(dram_pct, float) and dram_pct > 60.0:
        highlights.append("DRAM throughput is high enough to suggest memory pressure.")

    if top_events:
        top = top_events[0]
        if frame_time_ms and top["time_ms"] >= frame_time_ms * 0.25:
            highlights.append(
                f"Largest GPU event is '{top['event']}' at {top['time_ms']:.3f} ms."
            )

    return highlights
