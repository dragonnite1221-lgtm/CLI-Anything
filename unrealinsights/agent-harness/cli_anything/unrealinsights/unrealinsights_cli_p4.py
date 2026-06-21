# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _human_ensure_insights, _human_trace_info, _output  # noqa: E402,E501
from .unrealinsights_cli_p2 import _human_store_info, _human_store_latest, _human_store_list  # noqa: E402,E501
from .unrealinsights_cli_p3 import backend_group, cli  # noqa: E402,E501
# fmt: on


@backend_group.command("ensure-insights")
@click.option("--engine-root", required=True, type=click.Path(exists=False), help="UE install root or its Engine subdir.")
@click.option(
    "--build-if-missing/--no-build-if-missing",
    default=True,
    show_default=True,
    help="Build UnrealInsights when it is missing under the given engine root.",
)
@click.option("--configuration", default="Development", show_default=True, help="Build configuration.")
@click.option("--timeout", type=float, default=None, help="Optional build timeout in seconds.")
@click.pass_context
def backend_ensure_insights(ctx, engine_root, build_if_missing, configuration, timeout):
    """Find or build UnrealInsights.exe for a specific engine root."""
    try:
        data = ensure_engine_unrealinsights(
            engine_root,
            build_if_missing=build_if_missing,
            configuration=configuration,
            timeout=timeout,
        )
        session = _get_session(ctx)
        session.set_insights_exe(data["insights"]["path"])
        trace_server = data.get("trace_server")
        if trace_server and trace_server.get("available"):
            session.set_trace_server_exe(trace_server["path"])
        _output(ctx, data, _human_ensure_insights)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("trace")
def trace_group():
    """Session trace path management."""
@trace_group.command("set")
@click.argument("trace_path", type=click.Path(exists=False))
@click.pass_context
def trace_set(ctx, trace_path):
    """Set the active trace path for this session or REPL."""
    session = _get_session(ctx)
    session.set_trace(trace_path)
    _output(ctx, session.trace_info(), _human_trace_info)
@trace_group.command("info")
@click.pass_context
def trace_info(ctx):
    """Show the active trace path."""
    session = _get_session(ctx)
    _output(ctx, session.trace_info(), _human_trace_info)
@cli.group("store")
def store_group():
    """Trace Store discovery and session selection."""
@store_group.command("info")
@click.option("--store-dir", type=click.Path(exists=False), default=None, help="Explicit Trace Store directory.")
@click.pass_context
def store_info(ctx, store_dir):
    """Inspect the local Unreal Trace Store."""
    try:
        session = _get_session(ctx)
        data = trace_store_info(store_dir=store_dir, trace_server_exe=session.trace_server_exe)
        _output(ctx, data, _human_store_info)
    except Exception as exc:
        _handle_exc(ctx, exc)
@store_group.command("list")
@click.option("--store-dir", type=click.Path(exists=False), default=None, help="Explicit Trace Store directory.")
@click.option("--live-only", is_flag=True, help="Only show recently modified trace files.")
@click.option("--include-cache/--no-include-cache", default=True, show_default=True, help="Include Trace Store .ucache files.")
@click.option("--live-window", type=float, default=60.0, show_default=True, help="Seconds used for live-candidate detection.")
@click.pass_context
def store_list(ctx, store_dir, live_only, include_cache, live_window):
    """List trace files in the Trace Store."""
    try:
        data = list_trace_files(
            store_dir=store_dir,
            live_only=live_only,
            include_cache=include_cache,
            live_window_seconds=live_window,
        )
        _output(ctx, data, _human_store_list)
    except Exception as exc:
        _handle_exc(ctx, exc)
@store_group.command("latest")
@click.option("--store-dir", type=click.Path(exists=False), default=None, help="Explicit Trace Store directory.")
@click.option("--live-only", is_flag=True, help="Only consider recently modified trace files.")
@click.option("--include-cache/--no-include-cache", default=True, show_default=True, help="Include Trace Store .ucache files.")
@click.option("--live-window", type=float, default=60.0, show_default=True, help="Seconds used for live-candidate detection.")
@click.option("--set-current", is_flag=True, help="Set the selected trace as the current session trace.")
@click.pass_context
def store_latest(ctx, store_dir, live_only, include_cache, live_window, set_current):
    """Select the newest trace file in the Trace Store."""
    try:
        data = latest_trace_file(
            store_dir=store_dir,
            live_only=live_only,
            include_cache=include_cache,
            live_window_seconds=live_window,
        )
        latest = data.get("latest")
        if latest and set_current:
            _get_session(ctx).set_trace(latest["path"])
            data["set_current"] = True
        else:
            data["set_current"] = False
        _output(ctx, data, _human_store_latest)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("capture")
def capture_group():
    """Trace capture orchestration."""
