# ruff: noqa: F403, F405, E501
from .gpu_trace_base import *  # noqa: F403

# fmt: off
from .gpu_trace_p4 import summarize_export_dir  # noqa: E402,E501
# fmt: on


def capture_trace(
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
    start_after_frames: int | None,
    start_after_submits: int | None,
    start_after_ms: int | None,
    start_after_hotkey: bool,
    max_duration_ms: int | None,
    limit_to_frames: int | None,
    limit_to_submits: int | None,
    auto_export: bool,
    architecture: str | None,
    metric_set_id: str | None,
    multi_pass_metrics: bool,
    real_time_shader_profiler: bool,
    summarize: bool = False,
    summary_limit: int = 10,
) -> dict:
    """Run a GPU Trace capture."""
    output_dir = backend.prepare_output_dir(output_dir)
    report = backend.probe_installation(nsight_path=nsight_path)
    binaries = report["binaries"]
    backend.require_binary(binaries, "ngfx")
    backend.require_launch_target(project=project, exe=exe)

    backend.ensure_exactly_one(
        "gpu trace start trigger",
        {
            "start_after_frames": start_after_frames is not None,
            "start_after_submits": start_after_submits is not None,
            "start_after_ms": start_after_ms is not None,
            "start_after_hotkey": start_after_hotkey,
        },
    )
    backend.ensure_at_most_one(
        "gpu trace stop limit",
        {
            "limit_to_frames": limit_to_frames is not None,
            "limit_to_submits": limit_to_submits is not None,
        },
    )
    if metric_set_id and not architecture:
        raise ValueError("--metric-set-id requires --architecture.")
    if summary_limit < 1:
        raise ValueError("--summary-limit must be at least 1.")

    auto_export = auto_export or summarize

    extra_args: list[str] = []
    if start_after_frames is not None:
        extra_args.extend(["--start-after-frames", str(start_after_frames)])
    elif start_after_submits is not None:
        extra_args.extend(["--start-after-submits", str(start_after_submits)])
    elif start_after_ms is not None:
        extra_args.extend(["--start-after-ms", str(start_after_ms)])
    else:
        extra_args.append("--start-after-hotkey")

    if max_duration_ms is not None:
        extra_args.extend(["--max-duration-ms", str(max_duration_ms)])
    if limit_to_frames is not None:
        extra_args.extend(["--limit-to-frames", str(limit_to_frames)])
    if limit_to_submits is not None:
        extra_args.extend(["--limit-to-submits", str(limit_to_submits)])
    if auto_export:
        extra_args.append("--auto-export")
    if architecture:
        extra_args.extend(["--architecture", architecture])
    if metric_set_id:
        extra_args.extend(["--metric-set-id", str(metric_set_id)])
    if multi_pass_metrics:
        extra_args.append("--multi-pass-metrics")
    if real_time_shader_profiler:
        extra_args.append("--real-time-shader-profiler")

    command = backend.build_unified_command(
        binaries,
        activity="GPU Trace Profiler",
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
        output_roots=backend.activity_artifact_roots("GPU Trace Profiler", output_dir),
        timeout=600,
    )
    result["tool_mode"] = "unified"
    result["activity"] = "GPU Trace Profiler"
    result["output_dir"] = output_dir or backend.default_output_dir()
    result["auto_export"] = auto_export

    if summarize:
        if not result.get("ok"):
            raise RuntimeError(
                "GPU Trace capture failed; refusing to summarize stale export tables. "
                f"stderr: {result.get('stderr') or '<empty>'}"
            )
        artifact_paths = [item["path"] for item in result.get("artifacts", [])]
        result["summary"] = summarize_export_dir(
            result["output_dir"],
            top_n=summary_limit,
            artifact_paths=artifact_paths,
        )
    return result
