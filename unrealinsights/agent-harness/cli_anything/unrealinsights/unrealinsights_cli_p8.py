# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _handle_exc, _human_export_result, _output, _require_trace, _resolve_insights  # noqa: E402,E501
from .unrealinsights_cli_p3 import cli  # noqa: E402,E501
from .unrealinsights_cli_p7 import _run_export, export_group  # noqa: E402,E501
# fmt: on


@export_group.command("timer-stats")
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--columns", default=None)
@click.option("--threads", default=None)
@click.option("--timers", default=None)
@click.option("--start-time", type=float, default=None)
@click.option("--end-time", type=float, default=None)
@click.option("--region", default=None)
@click.pass_context
def export_timer_stats(ctx, output_path, columns, threads, timers, start_time, end_time, region):
    """Export aggregated timer statistics."""
    try:
        _run_export(
            ctx,
            "timer-stats",
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
@export_group.command("timer-callees")
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--threads", default=None)
@click.option("--timers", default=None)
@click.option("--start-time", type=float, default=None)
@click.option("--end-time", type=float, default=None)
@click.option("--region", default=None)
@click.pass_context
def export_timer_callees(ctx, output_path, threads, timers, start_time, end_time, region):
    """Export timer callee trees."""
    try:
        _run_export(
            ctx,
            "timer-callees",
            output_path,
            threads=threads,
            timers=timers,
            start_time=start_time,
            end_time=end_time,
            region=region,
        )
    except Exception as exc:
        _handle_exc(ctx, exc)
@export_group.command("counters")
@click.argument("output_path", type=click.Path(exists=False))
@click.pass_context
def export_counters(ctx, output_path):
    """Export the counter list."""
    try:
        _run_export(ctx, "counters", output_path)
    except Exception as exc:
        _handle_exc(ctx, exc)
@export_group.command("counter-values")
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--counter", default=None)
@click.option("--columns", default=None)
@click.option("--start-time", type=float, default=None)
@click.option("--end-time", type=float, default=None)
@click.option("--region", default=None)
@click.pass_context
def export_counter_values(ctx, output_path, counter, columns, start_time, end_time, region):
    """Export counter values."""
    try:
        _run_export(
            ctx,
            "counter-values",
            output_path,
            counter=counter,
            columns=columns,
            start_time=start_time,
            end_time=end_time,
            region=region,
        )
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("batch")
def batch_group():
    """Batch export workflows."""
@batch_group.command("run-rsp")
@click.argument("rsp_path", type=click.Path(exists=False))
@click.pass_context
def batch_run_rsp(ctx, rsp_path):
    """Execute a response file using UnrealInsights.exe."""
    try:
        trace_path = _require_trace(ctx)
        insights = _resolve_insights(ctx)
        data = execute_response_file(
            insights["path"],
            trace_path,
            rsp_path,
            insights_version=insights.get("version"),
        )
        _output(ctx, data, _human_export_result)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("analyze")
def analyze_group():
    """Export and summarize Unreal Insights timing/counter data."""
