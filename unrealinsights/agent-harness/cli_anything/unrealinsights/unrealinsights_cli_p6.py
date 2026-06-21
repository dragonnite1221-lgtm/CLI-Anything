# ruff: noqa: F403, F405, E501
from .unrealinsights_cli_base import *  # noqa: F403
# fmt: off
from .unrealinsights_cli_p1 import _get_session, _handle_exc, _output  # noqa: E402,E501
from .unrealinsights_cli_p2 import _human_live_result, _human_processes, _human_snapshot_result, _human_stop_result  # noqa: E402,E501
from .unrealinsights_cli_p3 import cli  # noqa: E402,E501
from .unrealinsights_cli_p4 import capture_group  # noqa: E402,E501
# fmt: on


@capture_group.command("stop")
@click.option("--force", is_flag=True, help="Force terminate the process tree.")
@click.option("--timeout", type=float, default=None, help="Optional stop timeout in seconds.")
@click.pass_context
def capture_stop_cmd(ctx, force, timeout):
    """Stop the tracked capture process."""
    try:
        data = stop_capture(_get_session(ctx), force=force, timeout=timeout)
        _output(ctx, data, _human_stop_result)
    except Exception as exc:
        _handle_exc(ctx, exc)
@capture_group.command("snapshot")
@click.argument("output_trace", required=False, type=click.Path(exists=False))
@click.pass_context
def capture_snapshot_cmd(ctx, output_trace):
    """Create a best-effort snapshot copy of the current trace."""
    try:
        data = snapshot_capture(_get_session(ctx), output_trace=output_trace)
        _output(ctx, data, _human_snapshot_result)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("live")
def live_group():
    """Live UE process discovery and trace-control command delivery."""
@live_group.command("processes")
@click.option("--include-tools/--no-include-tools", default=True, show_default=True, help="Include UnrealInsights and TraceServer.")
@click.pass_context
def live_processes(ctx, include_tools):
    """List local Unreal-related processes."""
    try:
        data = list_unreal_processes(include_tools=include_tools)
        _output(ctx, data, _human_processes)
    except Exception as exc:
        _handle_exc(ctx, exc)
def _run_live_command(ctx: click.Context, fn, *args, backend_command=None, timeout=None):
    data = fn(*args, backend_command=backend_command, timeout=timeout)
    _output(ctx, data, _human_live_result)
@live_group.command("exec")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.argument("command", nargs=-1, required=True)
@click.pass_context
def live_exec(ctx, pid, backend_command, timeout, command):
    """Send a raw console command to a live UE process."""
    try:
        data = execute_live_command(
            pid,
            " ".join(command),
            backend_command=backend_command,
            timeout=timeout,
        )
        _output(ctx, data, _human_live_result)
    except Exception as exc:
        _handle_exc(ctx, exc)
@live_group.command("trace-status")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.pass_context
def live_trace_status_cmd(ctx, pid, backend_command, timeout):
    """Run Trace.Status on a live UE process."""
    try:
        _run_live_command(ctx, live_trace_status, pid, backend_command=backend_command, timeout=timeout)
    except Exception as exc:
        _handle_exc(ctx, exc)
@live_group.command("bookmark")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.argument("name")
@click.pass_context
def live_bookmark(ctx, pid, backend_command, timeout, name):
    """Insert a Trace.Bookmark marker in a live UE process."""
    try:
        _run_live_command(ctx, trace_bookmark, pid, name, backend_command=backend_command, timeout=timeout)
    except Exception as exc:
        _handle_exc(ctx, exc)
@live_group.command("screenshot")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.argument("name")
@click.pass_context
def live_screenshot(ctx, pid, backend_command, timeout, name):
    """Insert a Trace.Screenshot marker in a live UE process."""
    try:
        _run_live_command(ctx, trace_screenshot, pid, name, backend_command=backend_command, timeout=timeout)
    except Exception as exc:
        _handle_exc(ctx, exc)
@live_group.command("snapshot")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.argument("output_trace", type=click.Path(exists=False))
@click.pass_context
def live_snapshot(ctx, pid, backend_command, timeout, output_trace):
    """Request a Trace.SnapshotFile from a live UE process."""
    try:
        _run_live_command(ctx, trace_snapshot, pid, output_trace, backend_command=backend_command, timeout=timeout)
    except Exception as exc:
        _handle_exc(ctx, exc)
@live_group.command("stop-trace")
@click.option("--pid", required=True, type=int, help="Target UE process id.")
@click.option("--backend-command", default=None, help="External command template accepting {pid} and {cmd}.")
@click.option("--timeout", type=float, default=None, help="Optional backend timeout in seconds.")
@click.pass_context
def live_stop_trace(ctx, pid, backend_command, timeout):
    """Stop tracing in a live UE process without killing the process."""
    try:
        _run_live_command(ctx, trace_stop, pid, backend_command=backend_command, timeout=timeout)
    except Exception as exc:
        _handle_exc(ctx, exc)
@cli.group("gui")
def gui_group():
    """Unreal Insights GUI co-pilot helpers."""
