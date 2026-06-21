# ruff: noqa: F403, F405, E501
from .frame_base import *  # noqa: F403


def _select_frame_activity(report: dict, requested_activity: str | None) -> str:
    """Choose a frame capture activity that matches the installed Nsight version."""
    if requested_activity:
        return requested_activity

    supported = set(report.get("supported_activities") or [])
    for candidate in (
        GRAPHICS_CAPTURE_ACTIVITY,
        LEGACY_FRAME_ACTIVITY,
        OPENGL_FRAME_ACTIVITY,
    ):
        if candidate in supported:
            return candidate
    return GRAPHICS_CAPTURE_ACTIVITY


def _activity_options(report: dict, activity: str) -> set[str]:
    """Return known options for a parsed ngfx activity."""
    return set((report.get("activity_options") or {}).get(activity, []))


def _append_if_supported(
    extra_args: list[str],
    *,
    report: dict,
    activity: str,
    option: str,
    enabled: bool,
) -> None:
    """Append an option only when this Nsight activity advertises it."""
    if not enabled:
        return
    if option not in _activity_options(report, activity):
        raise RuntimeError(
            f"{option} is not supported by Nsight activity '{activity}'."
        )
    extra_args.append(option)


def _build_unified_frame_args(
    *,
    report: dict,
    activity: str,
    wait_seconds: int | None,
    wait_frames: int | None,
    wait_hotkey: bool,
    export_frame_perf_metrics: bool,
    export_range_perf_metrics: bool,
) -> list[str]:
    """Map the harness trigger vocabulary onto the selected ngfx activity."""
    backend.ensure_exactly_one(
        "frame trigger",
        {
            "wait_seconds": wait_seconds is not None,
            "wait_frames": wait_frames is not None,
            "wait_hotkey": wait_hotkey,
        },
    )

    options = _activity_options(report, activity)
    extra_args: list[str] = []
    if activity == GRAPHICS_CAPTURE_ACTIVITY or "--frame-index" in options:
        extra_args.extend(["--frame-count", "1"])
        if wait_seconds is not None:
            extra_args.extend(["--elapsed-time", str(wait_seconds)])
        elif wait_frames is not None:
            extra_args.extend(["--frame-index", str(wait_frames)])
        else:
            extra_args.append("--hotkey-capture")
    else:
        if wait_seconds is not None:
            extra_args.extend(["--wait-seconds", str(wait_seconds)])
        elif wait_frames is not None:
            extra_args.extend(["--wait-frames", str(wait_frames)])
        else:
            extra_args.append("--wait-hotkey")

    _append_if_supported(
        extra_args,
        report=report,
        activity=activity,
        option="--export-frame-perf-metrics",
        enabled=export_frame_perf_metrics,
    )
    _append_if_supported(
        extra_args,
        report=report,
        activity=activity,
        option="--export-range-perf-metrics",
        enabled=export_range_perf_metrics,
    )
    return extra_args
