# ruff: noqa: F403, F405, E501
from .analyze_base import *  # noqa: F403

# fmt: off
from .analyze_p1 import _counter_summaries, _diagnostics, _export_statuses, _read_csv_rows, _timer_entry, _top_entries  # noqa: E402,E501
# fmt: on


def summarize_exports(
    out_dir: str,
    *,
    trace_path: str | None = None,
    export_results: list[dict[str, object]] | None = None,
    limit: int = 20,
    focus_threads: Iterable[str] = DEFAULT_FOCUS_THREADS,
) -> dict[str, object]:
    """Summarize exported Unreal Insights CSV files."""
    root = Path(out_dir).expanduser().resolve()
    timer_rows = _read_csv_rows(root / "timer_stats.csv") or _read_csv_rows(
        root / "timers.csv"
    )
    counter_rows = _read_csv_rows(root / "counter_values.csv")
    timer_entries = [_timer_entry(row) for row in timer_rows]

    focus = {}
    for thread in focus_threads:
        token = thread.lower()
        focus[thread] = _top_entries(
            [
                entry
                for entry in timer_entries
                if token in str(entry.get("thread") or "").lower()
                or token in str(entry.get("name") or "").lower()
            ],
            limit,
        )

    wait_entries = [
        entry
        for entry in timer_entries
        if any(token in str(entry.get("name") or "").lower() for token in WAIT_TOKENS)
    ]

    warnings = []
    if not timer_entries:
        warnings.append("No timer statistics CSV was found or parsed.")
    if not counter_rows:
        warnings.append("No counter values CSV was found or parsed.")

    top_timers = _top_entries(timer_entries, limit)
    wait_timers = _top_entries(wait_entries, limit)
    counter_peaks = _counter_summaries(counter_rows, limit)
    export_status = _export_statuses(export_results)

    return {
        "trace_path": str(Path(trace_path).expanduser().resolve())
        if trace_path
        else None,
        "out_dir": str(root),
        "exports": export_results or [],
        "export_status": export_status,
        "summary": {
            "top_timers": top_timers,
            "focus_threads": focus,
            "wait_timers": wait_timers,
            "counter_peaks": counter_peaks,
            "diagnostics": _diagnostics(
                top_timers, focus, wait_timers, counter_peaks, export_status
            ),
            "uncovered_domains": UNCOVERED_DOMAINS,
        },
        "warnings": warnings,
        "succeeded": bool(timer_entries or counter_rows),
    }


def run_summary_exports(
    insights_exe: str,
    trace_path: str,
    out_dir: str,
    *,
    insights_version: str | None = None,
) -> list[dict[str, object]]:
    """Run the standard exporter bundle used by analyze summary."""
    root = Path(out_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    results = []
    for exporter, filename, options in SUMMARY_EXPORTS:
        result = execute_export(
            insights_exe,
            trace_path,
            exporter,
            str(root / filename),
            insights_version=insights_version,
            **options,
        )
        results.append(result)
    return results


def analyze_summary(
    insights_exe: str | None,
    trace_path: str | None,
    out_dir: str,
    *,
    insights_version: str | None = None,
    skip_export: bool = False,
    limit: int = 20,
) -> dict[str, object]:
    """Run exports when requested, then summarize the export directory."""
    export_results: list[dict[str, object]] = []
    if not skip_export:
        if not insights_exe:
            raise RuntimeError(
                "UnrealInsights.exe is required unless --skip-export is used."
            )
        if not trace_path:
            raise RuntimeError("A trace path is required unless --skip-export is used.")
        export_results = run_summary_exports(
            insights_exe,
            trace_path,
            out_dir,
            insights_version=insights_version,
        )

    summary = summarize_exports(
        out_dir,
        trace_path=trace_path,
        export_results=export_results,
        limit=limit,
    )
    if export_results:
        summary["succeeded"] = (
            any(result.get("succeeded") for result in export_results)
            and summary["succeeded"]
        )
    return summary
