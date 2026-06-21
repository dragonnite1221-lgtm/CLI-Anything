# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403


def _output(ctx: click.Context, data, human_fn=None):
    if ctx.obj.get("json_mode"):
        from cli_anything.nsight_graphics.utils.output import output_json

        output_json(data)
    elif human_fn:
        human_fn(data)
    else:
        from cli_anything.nsight_graphics.utils.output import output_json

        output_json(data)


def _handle_exc(ctx: click.Context, exc: Exception):
    from cli_anything.nsight_graphics.utils.errors import handle_error

    payload = handle_error(exc, debug=ctx.obj.get("debug", False))
    if ctx.obj.get("json_mode"):
        from cli_anything.nsight_graphics.utils.output import output_json

        output_json(payload)
        ctx.exit(1)
    raise click.ClickException(payload["error"])


def _common_kwargs(ctx: click.Context) -> dict:
    return {
        "nsight_path": ctx.obj.get("nsight_path"),
        "project": ctx.obj.get("project"),
        "output_dir": ctx.obj.get("output_dir"),
        "hostname": ctx.obj.get("hostname"),
        "platform_name": ctx.obj.get("platform_name"),
    }


def _print_gpu_trace_summary(summary: dict) -> None:
    """Render a compact human-readable GPU Trace summary."""
    frame_time = summary.get("frame_time_ms")
    fps = summary.get("fps_estimate")
    if frame_time is not None:
        click.echo(f"Frame time: {frame_time:.3f} ms")
    if fps is not None:
        click.echo(f"Estimated FPS: {fps:.2f}")

    metrics = summary.get("metrics", {})
    if metrics:
        click.echo("Metrics:")
        for label, key in [
            ("Draws", "draw_count"),
            ("Dispatches", "dispatch_count"),
            ("Graphics active %", "graphics_engine_active_pct"),
            ("Compute sync active %", "compute_queue_sync_active_pct"),
            ("SM throughput %", "sm_throughput_pct"),
            ("L2 throughput %", "l2_throughput_pct"),
            ("DRAM throughput %", "dram_throughput_pct"),
        ]:
            value = metrics.get(key)
            if value is None:
                continue
            if isinstance(value, float):
                click.echo(f"  {label}: {value:.3f}")
            else:
                click.echo(f"  {label}: {value}")

    top_events = summary.get("top_events", [])
    if top_events:
        click.echo("Top GPU events:")
        for item in top_events:
            click.echo(f"  - {item['event']}: {item['time_ms']:.3f} ms")

    highlights = summary.get("highlights", [])
    if highlights:
        click.echo("Highlights:")
        for line in highlights:
            click.echo(f"  - {line}")


def _print_replay_analysis(payload: dict) -> None:
    """Render a compact human-readable replay analysis summary."""
    click.echo(f"Capture: {payload.get('capture_file')}")
    click.echo(f"Type:    {payload.get('capture_type')}")
    click.echo(f"Output:  {payload.get('output_dir')}")
    click.echo(f"Artifacts: {payload.get('artifact_count', 0)}")
    metadata_present = (payload.get("metadata") or {}).get("present") or {}
    if metadata_present:
        click.echo(
            "Metadata: "
            + ", ".join(
                f"{key}={'yes' if value else 'no'}"
                for key, value in metadata_present.items()
            )
        )
    errors = (payload.get("logs") or {}).get("error_summary") or []
    if errors:
        click.echo("Captured log errors:")
        for line in errors:
            click.echo(f"  - {line}")
