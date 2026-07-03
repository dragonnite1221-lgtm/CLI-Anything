"""Frame capture orchestration."""

from __future__ import annotations

from typing import Sequence

from cli_anything.nsight_graphics.utils import nsight_graphics_backend as backend
# Re-exported for backward compatibility (moved to frame_args.py).
from cli_anything.nsight_graphics.core.frame_args import (  # noqa: F401
    GRAPHICS_CAPTURE_ACTIVITY,
    LEGACY_FRAME_ACTIVITY,
    OPENGL_FRAME_ACTIVITY,
    _select_frame_activity,
    _activity_options,
    _append_if_supported,
    _build_unified_frame_args,
)


def capture_frame(
    *,
    nsight_path: str | None,
    project: str | None,
    output_dir: str | None,
    hostname: str | None,
    platform_name: str | None,
    exe: str | None,
    working_dir: str | None,
    args: Sequence[str],
    envs: Sequence[str],
    activity: str | None,
    wait_seconds: int | None,
    wait_frames: int | None,
    wait_hotkey: bool,
    export_frame_perf_metrics: bool,
    export_range_perf_metrics: bool,
) -> dict:
    """Run a Frame Debugger capture."""
    output_dir = backend.prepare_output_dir(output_dir)
    report = backend.probe_installation(nsight_path=nsight_path)
    binaries = report["binaries"]
    selected_activity = _select_frame_activity(report, activity)
    artifact_roots = backend._dedupe(
        backend.activity_artifact_roots(selected_activity, output_dir)
        + backend.activity_artifact_roots(selected_activity, None)
    )

    if binaries.get("ngfx"):
        backend.require_launch_target(project=project, exe=exe)
        extra_args = _build_unified_frame_args(
            report=report,
            activity=selected_activity,
            wait_seconds=wait_seconds,
            wait_frames=wait_frames,
            wait_hotkey=wait_hotkey,
            export_frame_perf_metrics=export_frame_perf_metrics,
            export_range_perf_metrics=export_range_perf_metrics,
        )

        command = backend.build_unified_command(
            binaries,
            activity=selected_activity,
            project=project,
            output_dir=output_dir,
            hostname=hostname,
            platform_name=platform_name,
            exe=exe,
            working_dir=working_dir,
            args=args,
            envs=envs,
            extra_args=extra_args,
        )
        result = backend.run_with_artifacts(
            command,
            output_roots=artifact_roots,
            timeout=300,
        )
        result["tool_mode"] = "unified"
    elif binaries.get("ngfx_capture"):
        if selected_activity != GRAPHICS_CAPTURE_ACTIVITY:
            raise RuntimeError(
                f"Activity '{selected_activity}' requires ngfx.exe; split ngfx-capture "
                "mode supports Graphics Capture only."
            )
        if project:
            raise RuntimeError(
                "Project-driven graphics capture fallback requires ngfx.exe; "
                "split ngfx-capture mode currently needs --exe."
            )
        if export_frame_perf_metrics or export_range_perf_metrics:
            raise RuntimeError(
                "Frame performance export flags require ngfx.exe Frame Debugger mode."
            )
        if not exe:
            raise ValueError("Specify --exe for split ngfx-capture mode.")

        command = backend.build_split_capture_command(
            binaries,
            exe=exe,
            output_dir=output_dir,
            working_dir=working_dir,
            args=args,
            envs=envs,
            wait_seconds=wait_seconds,
            wait_frames=wait_frames,
            wait_hotkey=wait_hotkey,
        )
        result = backend.run_with_artifacts(
            command,
            output_roots=artifact_roots,
            timeout=300,
        )
        result["tool_mode"] = "split"
    else:
        raise RuntimeError(backend.INSTALL_INSTRUCTIONS)

    result["activity"] = selected_activity
    result["output_dir"] = output_dir or backend.default_output_dir()
    return result
