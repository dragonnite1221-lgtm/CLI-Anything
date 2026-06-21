# ruff: noqa: F403, F405, E501
from .analyze_base import *  # noqa: F403


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _field(row: dict[str, str], candidates: Iterable[str]) -> str | None:
    normalized = {_normalize_header(key): key for key in row.keys()}
    for candidate in candidates:
        key = normalized.get(_normalize_header(candidate))
        if key is not None:
            return row.get(key)
    for norm_key, original in normalized.items():
        if any(_normalize_header(candidate) in norm_key for candidate in candidates):
            return row.get(original)
    return None


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().replace(",", "")
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _timer_entry(row: dict[str, str]) -> dict[str, object]:
    name = (
        _field(row, ("Timer Name", "TimerName", "Name", "Timer", "EventName"))
        or "unknown"
    )
    thread = _field(row, ("Thread", "Thread Name", "ThreadName", "ThreadId"))
    count = _number(_field(row, ("Count", "Num Calls", "Calls", "Instance Count")))
    inclusive = _number(
        _field(row, ("Inclusive Time", "InclusiveTime", "Incl Time", "Total Incl Time"))
    )
    exclusive = _number(
        _field(row, ("Exclusive Time", "ExclusiveTime", "Excl Time", "Total Excl Time"))
    )
    total = _number(_field(row, ("Total Time", "TotalTime", "Duration", "Time", "Sum")))
    score = (
        total
        if total is not None
        else inclusive
        if inclusive is not None
        else exclusive
        if exclusive is not None
        else count or 0.0
    )
    return {
        "name": name,
        "thread": thread,
        "count": count,
        "total_time": total,
        "inclusive_time": inclusive,
        "exclusive_time": exclusive,
        "score": score,
    }


def _top_entries(
    entries: list[dict[str, object]], limit: int
) -> list[dict[str, object]]:
    return sorted(
        entries, key=lambda item: float(item.get("score") or 0.0), reverse=True
    )[:limit]


def _counter_summaries(
    rows: list[dict[str, str]], limit: int
) -> list[dict[str, object]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        name = (
            _field(row, ("Counter", "Counter Name", "CounterName", "Name")) or "unknown"
        )
        value = _number(_field(row, ("Value", "Counter Value", "CounterValue")))
        if value is not None:
            grouped[name].append(value)

    summaries = []
    for name, values in grouped.items():
        summaries.append(
            {
                "name": name,
                "samples": len(values),
                "min": min(values),
                "max": max(values),
                "last": values[-1],
                "score": max(values),
            }
        )
    return _top_entries(summaries, limit)


def _status_counts(export_status: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in export_status:
        counts[str(item.get("status") or "unknown")] += 1
    return dict(counts)


def _diagnostics(
    top_timers: list[dict[str, object]],
    focus: dict[str, list[dict[str, object]]],
    wait_timers: list[dict[str, object]],
    counter_peaks: list[dict[str, object]],
    export_status: list[dict[str, object]],
) -> dict[str, object]:
    active_threads = [thread for thread, entries in focus.items() if entries]
    counter_anomalies = [
        counter
        for counter in counter_peaks
        if counter.get("samples", 0) > 1 and counter.get("min") != counter.get("max")
    ]
    next_steps = []
    if top_timers:
        next_steps.append(f"Inspect the top timer `{top_timers[0]['name']}` first.")
    if wait_timers:
        next_steps.append(
            "Review wait/task timers for synchronization or scheduling stalls."
        )
    if counter_anomalies:
        next_steps.append(
            "Check counter peaks for transient spikes during the selected interval."
        )
    if not top_timers:
        next_steps.append(
            "Run exporter validation or provide a trace with timing data."
        )
    blocked_exports = [
        item for item in export_status if item.get("status") not in (None, "ok")
    ]
    if blocked_exports:
        next_steps.append(
            "Inspect export_status for exporters that produced no output or errors."
        )

    return {
        "primary_hotspot": top_timers[0] if top_timers else None,
        "active_focus_threads": active_threads,
        "wait_pressure": "present" if wait_timers else "none",
        "counter_anomaly_count": len(counter_anomalies),
        "counter_anomalies": counter_anomalies,
        "export_status_counts": _status_counts(export_status),
        "next_steps": next_steps,
    }


def _export_statuses(
    export_results: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    statuses = []
    for result in export_results or []:
        statuses.append(
            {
                "exporter": result.get("exporter") or "unknown",
                "status": result.get("output_status")
                or ("ok" if result.get("succeeded") else "unknown"),
                "succeeded": bool(result.get("succeeded")),
                "output_files": list(result.get("output_files") or []),
                "status_message": result.get("status_message"),
                "log_path": result.get("log_path"),
            }
        )
    return statuses
