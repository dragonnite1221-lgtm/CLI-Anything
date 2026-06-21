# ruff: noqa: F403, F405, E501
from .replay_base import *  # noqa: F403
# fmt: off
from .replay_p3 import _run_stdout_export, _summarize_logs  # noqa: E402,E501
# fmt: on


def _build_analysis(
    *,
    capture_kind: str,
    metadata_requested: bool,
    logs_requested: bool,
    screenshot_requested: bool,
    perf_requested: bool,
    metadata_present: dict[str, bool],
    metadata_summary: dict[str, Any],
    object_summary: dict[str, Any],
    function_summary: dict[str, Any],
    logs_summary: dict[str, Any],
    screenshot_payload: dict[str, Any],
    perf_payload: dict[str, Any],
    command_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a compact human-usable diagnosis layer over replay artifacts."""
    highlights: list[str] = []
    warnings: list[str] = []

    if capture_kind == "gpu_trace":
        warnings.append(
            "ngfx-replay metadata is documented for graphics capture files; "
            ".ngfx-gputrace inputs may not produce metadata on this Nsight version."
        )

    failed = [item["kind"] for item in command_results if not item.get("ok")]
    if failed:
        warnings.append(f"Replay command failures: {', '.join(failed)}.")

    if metadata_requested:
        if metadata_summary.get("primary_api"):
            highlights.append(f"Primary API: {metadata_summary['primary_api']}.")
        if metadata_summary.get("primary_gpu"):
            highlights.append(f"Primary GPU: {metadata_summary['primary_gpu']}.")
        if object_summary.get("total"):
            highlights.append(f"Metadata objects: {object_summary['total']}.")
        if function_summary.get("total"):
            highlights.append(f"Function events: {function_summary['total']}.")
        if not any(metadata_present.values()):
            warnings.append("No replay metadata artifacts were produced.")

    if logs_requested:
        if logs_summary.get("error_line_count"):
            warnings.append(f"Captured log errors: {logs_summary['error_line_count']}.")
        elif logs_summary.get("status") == "no_errors":
            highlights.append("Captured replay logs reported no severity >= 2 errors.")

    if screenshot_requested:
        if screenshot_payload.get("present"):
            highlights.append("Metadata screenshot exported.")
        else:
            warnings.append("Metadata screenshot was requested but no non-empty image was produced.")

    if perf_requested:
        if perf_payload.get("present"):
            highlights.append("Replay performance report exported.")
        else:
            warnings.append("Performance report was requested but no non-empty report files were produced.")

    return {
        "summary": {
            "metadata_artifacts_present": metadata_present,
            "primary_api": metadata_summary.get("primary_api"),
            "primary_gpu": metadata_summary.get("primary_gpu"),
            "object_count": object_summary.get("total", 0),
            "function_event_count": function_summary.get("total", 0),
            "log_error_count": logs_summary.get("error_line_count", 0),
            "screenshot_present": screenshot_payload.get("present", False),
            "perf_report_present": perf_payload.get("present", False),
        },
        "highlights": highlights,
        "warnings": warnings,
    }
def _analyze_logs(binaries, capture_path, command_results, logs, logs_payload, output_root):
    if logs:
        log_file = output_root / "metadata_logs.txt"
        errors_file = output_root / "metadata_log_errors.txt"
        command_results.append(
            _run_stdout_export(
                binaries,
                capture_file=str(capture_path),
                output_file=log_file,
                kind="metadata_logs",
                replay_flag="--metadata-logs",
            )
        )
        command_results.append(
            _run_stdout_export(
                binaries,
                capture_file=str(capture_path),
                output_file=errors_file,
                kind="metadata_log_errors",
                replay_flag="--metadata-logs-errors",
            )
        )
        logs_payload["log_file"] = str(log_file) if log_file.is_file() else None
        logs_payload["errors_file"] = str(errors_file) if errors_file.is_file() else None
        logs_payload.update(_summarize_logs(log_file, errors_file))
