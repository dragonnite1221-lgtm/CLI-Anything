# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _human_export_result, _output, _require_trace, _resolve_insights  # noqa: E402,E501
from .unrealinsights_cli_p2 import _human_gui_open, _human_gui_status  # noqa: E402,E501
from .unrealinsights_cli_p3 import cli  # noqa: E402,E501
from .unrealinsights_cli_p6 import gui_group  # noqa: E402,E501
# fmt: on


@gui_group.command("status")
@click.pass_context
def gui_status_cmd(ctx):
    """Show running Unreal Insights GUI processes."""
    try:
        data = gui_status()
        _output(ctx, data, _human_gui_status)
    except Exception as exc:
        _handle_exc(ctx, exc)
@gui_group.command("open")
@click.option("--trace", "trace_override", type=click.Path(exists=False), default=None, help="Trace file to open in the GUI.")
@click.pass_context
def gui_open_cmd(ctx, trace_override):
    """Open Unreal Insights GUI and keep it running."""
    try:
        trace_path = trace_override or _get_session(ctx).trace_path
        insights = _resolve_insights(ctx)
        data = open_gui(insights["path"], trace_path=trace_path)
        _output(ctx, data, _human_gui_open)
    except Exception as exc:
        _handle_exc(ctx, exc)
@gui_group.command("open-latest")
@click.option("--store-dir", type=click.Path(exists=False), default=None, help="Explicit Trace Store directory.")
@click.option("--live-only", is_flag=True, help="Only consider recently modified trace files.")
@click.option("--include-cache/--no-include-cache", default=True, show_default=True, help="Include Trace Store .ucache files.")
@click.pass_context
def gui_open_latest(ctx, store_dir, live_only, include_cache):
    """Open the newest Trace Store trace in Unreal Insights GUI."""
    try:
        latest = latest_trace_file(store_dir=store_dir, live_only=live_only, include_cache=include_cache).get("latest")
        if not latest:
            raise RuntimeError("No trace file found in the Trace Store.")
        _get_session(ctx).set_trace(latest["path"])
        insights = _resolve_insights(ctx)
        data = open_gui(insights["path"], trace_path=latest["path"])
        data["latest"] = latest
        _output(ctx, data, _human_gui_open)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("export")
def export_group():
    """Offline Unreal Insights exporters."""
def _run_export(
    ctx: click.Context,
    exporter: str,
    output_path: str,
    *,
    columns: str | None = None,
    threads: str | None = None,
    timers: str | None = None,
    start_time: float | None = None,
    end_time: float | None = None,
    region: str | None = None,
    counter: str | None = None,
):
    trace_path = _require_trace(ctx)
    insights = _resolve_insights(ctx)
    data = execute_export(
        insights["path"],
        trace_path,
        exporter,
        output_path,
        insights_version=insights.get("version"),
        columns=columns,
        threads=threads,
        timers=timers,
        start_time=start_time,
        end_time=end_time,
        region=region,
        counter=counter,
    )
    _output(ctx, data, _human_export_result)
@export_group.command("threads")
@click.argument("output_path", type=click.Path(exists=False))
@click.pass_context
def export_threads(ctx, output_path):
    """Export thread metadata."""
    try:
        _run_export(ctx, "threads", output_path)
    except Exception as exc:
        _handle_exc(ctx, exc)
@export_group.command("timers")
@click.argument("output_path", type=click.Path(exists=False))
@click.pass_context
def export_timers(ctx, output_path):
    """Export timer metadata."""
    try:
        _run_export(ctx, "timers", output_path)
    except Exception as exc:
        _handle_exc(ctx, exc)
@export_group.command("timing-events")
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--columns", default=None)
@click.option("--threads", default=None)
@click.option("--timers", default=None)
@click.option("--start-time", type=float, default=None)
@click.option("--end-time", type=float, default=None)
@click.option("--region", default=None)
@click.pass_context
def export_timing_events(ctx, output_path, columns, threads, timers, start_time, end_time, region):
    """Export timing events."""
    try:
        _run_export(
            ctx,
            "timing-events",
            output_path,
            columns=columns,
            threads=threads,
            timers=timers,
            start_time=start_time,
            end_time=end_time,
            region=region,
        )
    except Exception as exc:
        _handle_exc(ctx, exc)
