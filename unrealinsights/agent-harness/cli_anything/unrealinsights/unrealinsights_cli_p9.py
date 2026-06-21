# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _output, _require_trace, _resolve_insights  # noqa: E402,E501
from .unrealinsights_cli_p2 import _human_analyze_summary  # noqa: E402,E501
from .unrealinsights_cli_p3 import cli  # noqa: E402,E501
from .unrealinsights_cli_p8 import analyze_group  # noqa: E402,E501
# fmt: on


@analyze_group.command("summary")
@click.option("--trace", "trace_override", type=click.Path(exists=False), default=None, help="Trace file to analyze.")
@click.option("--out", "out_dir", required=True, type=click.Path(exists=False), help="Directory for exports and summary inputs.")
@click.option("--skip-export", is_flag=True, help="Summarize existing CSV exports without launching UnrealInsights.exe.")
@click.option("--limit", type=int, default=20, show_default=True, help="Maximum entries per summary list.")
@click.pass_context
def analyze_summary_cmd(ctx, trace_override, out_dir, skip_export, limit):
    """Run the standard exporter bundle and summarize hot spots."""
    try:
        trace_path = None
        insights = None
        if trace_override:
            trace_path = str(Path(trace_override).expanduser().resolve())
            _get_session(ctx).set_trace(trace_path)
        elif not skip_export:
            trace_path = _require_trace(ctx)
        elif _get_session(ctx).trace_path:
            trace_path = _get_session(ctx).trace_path

        if not skip_export:
            insights = _resolve_insights(ctx)

        data = analyze_summary(
            insights["path"] if insights else None,
            trace_path,
            out_dir,
            insights_version=insights.get("version") if insights else None,
            skip_export=skip_export,
            limit=limit,
        )
        _output(ctx, data, _human_analyze_summary)
    except Exception as exc:
        _handle_exc(ctx, exc)
def main():
    cli(obj={})
