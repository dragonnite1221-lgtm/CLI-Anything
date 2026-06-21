# ruff: noqa: F403, F405, E501
from .gpu_trace_base import *  # noqa: F403

# fmt: off
from .gpu_trace_p1 import _metric_unit, _safe_float  # noqa: E402,E501
# fmt: on


def _metric_category(metric_name: str) -> str:
    """Classify a metric by GPU subsystem using stable metric prefixes."""
    lowered = metric_name.lower()
    if "pcie__" in lowered:
        return "pcie"
    if "dramc__" in lowered:
        return "dram"
    if "lts__" in lowered:
        return "l2_cache"
    if "l1tex__" in lowered:
        return "l1_texture"
    if "sm__" in lowered or "smsp__" in lowered or "tpc__" in lowered:
        return "shader_core"
    if (
        "crop__" in lowered
        or "zrop__" in lowered
        or "raster__" in lowered
        or "prop__" in lowered
        or "vaf__" in lowered
    ):
        return "raster_rop"
    if "fe__" in lowered:
        return "frontend"
    if "gr__" in lowered or "gpu__" in lowered:
        return "graphics_engine"
    return "other"


def _numeric_metrics(metrics: dict[str, str]) -> list[dict[str, Any]]:
    """Return metrics with parsed numeric values and basic classification."""
    parsed: list[dict[str, Any]] = []
    for key, value in metrics.items():
        numeric = _safe_float(value)
        if numeric is None:
            continue
        parsed.append(
            {
                "metric": key,
                "value": numeric,
                "unit": _metric_unit(key),
                "category": _metric_category(key),
            }
        )
    return parsed


def _top_numeric_metrics(
    parsed_metrics: list[dict[str, Any]],
    *,
    unit: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Return top numeric metrics for a unit family."""
    candidates = [item for item in parsed_metrics if item["unit"] == unit]
    candidates.sort(key=lambda item: abs(item["value"]), reverse=True)
    return candidates[:limit]


def _metric_inventory(metrics: dict[str, str], top_n: int) -> dict[str, Any]:
    """Summarize the exported GPU Trace metric table."""
    parsed = _numeric_metrics(metrics)
    return {
        "metric_count": len(metrics),
        "numeric_metric_count": len(parsed),
        "unit_counts": dict(Counter(item["unit"] for item in parsed)),
        "category_counts": dict(Counter(item["category"] for item in parsed)),
        "top_pct_of_peak_metrics": _top_numeric_metrics(
            parsed, unit="pct_of_peak", limit=top_n
        ),
        "top_count_metrics": _top_numeric_metrics(parsed, unit="count", limit=top_n),
    }


def _pick_metric(metrics: dict[str, str], needle: str) -> float | None:
    """Find the first metric whose key ends with the requested suffix."""
    for key, value in metrics.items():
        if key.endswith(needle):
            return _safe_float(value)
    return None


def _event_depth(event_text: str) -> int:
    """Compute indentation depth for an event row."""
    return len(event_text) - len(event_text.lstrip(" "))


def _table_file_info(path: str | None) -> dict[str, Any]:
    """Return compact file metadata for an optional table path."""
    if not path:
        return {"path": None, "present": False, "size": 0}
    table_path = Path(path)
    return {
        "path": str(table_path),
        "present": table_path.is_file(),
        "size": table_path.stat().st_size if table_path.is_file() else 0,
    }


def _table_inventory(
    *,
    files: dict[str, str | None],
    frame_data: dict[str, str],
    trace_metrics: dict[str, str],
    event_rows: list[dict[str, str]],
    regime_columns: list[str],
    regime_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """Describe exported tables and how much usable data they contain."""
    frame_info = _table_file_info(files["frame"])
    frame_info.update({"row_count": len(frame_data), "metric_count": len(frame_data)})

    trace_info = _table_file_info(files["trace_frame"])
    trace_info.update(
        {"row_count": len(trace_metrics), "metric_count": len(trace_metrics)}
    )

    events_info = _table_file_info(files["events"])
    events_info.update({"row_count": len(event_rows), "column_count": 2})

    regimes_info = _table_file_info(files.get("regimes"))
    regimes_info.update(
        {
            "row_count": len(regime_rows),
            "column_count": len(regime_columns),
            "metric_column_count": max(len(regime_columns) - 1, 0),
        }
    )

    return {
        "frame": frame_info,
        "trace_frame": trace_info,
        "events": events_info,
        "regimes": regimes_info,
    }


def _frame_budget(
    frame_time_ms: float | None, fps_estimate: float | None
) -> dict[str, Any]:
    """Classify frame time against common budgets."""
    if frame_time_ms is None:
        return {
            "frame_time_ms": None,
            "fps_estimate": fps_estimate,
            "bucket": "unknown",
            "over_60fps_budget_ms": None,
            "over_30fps_budget_ms": None,
        }
    return {
        "frame_time_ms": frame_time_ms,
        "fps_estimate": fps_estimate,
        "bucket": "over_30fps_budget"
        if frame_time_ms > 33.3
        else "over_60fps_budget"
        if frame_time_ms > 16.7
        else "within_60fps_budget",
        "over_60fps_budget_ms": max(frame_time_ms - 16.6667, 0.0),
        "over_30fps_budget_ms": max(frame_time_ms - 33.3333, 0.0),
    }


def _workload_classification(metrics: dict[str, float | int | None]) -> dict[str, Any]:
    """Classify draw/dispatch balance."""
    draw_count = metrics.get("draw_count")
    dispatch_count = metrics.get("dispatch_count")
    draw_count = draw_count if isinstance(draw_count, int) else 0
    dispatch_count = dispatch_count if isinstance(dispatch_count, int) else 0

    if dispatch_count > max(draw_count * 2, 500):
        classification = "compute_heavy"
    elif draw_count > max(dispatch_count * 2, 100):
        classification = "graphics_heavy"
    elif draw_count or dispatch_count:
        classification = "mixed"
    else:
        classification = "unknown"

    return {
        "classification": classification,
        "draw_count": draw_count,
        "dispatch_count": dispatch_count,
    }
