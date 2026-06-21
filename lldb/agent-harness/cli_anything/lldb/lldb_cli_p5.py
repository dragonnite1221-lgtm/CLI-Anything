# ruff: noqa: F403, F405, E501
from .lldb_cli_base import *  # noqa: F403

# fmt: off
from .lldb_cli_p1 import _get_session, _handle_exc, _output, _parse_int, _require_process, _require_target, _session_status, _shutdown_session, cli  # noqa: E402,E501
from .lldb_cli_p4 import memory_group  # noqa: E402,E501
# fmt: on


@memory_group.command("find")
@click.argument("needle", required=True, type=str)
@click.option(
    "--start", "start_addr", required=True, type=str, help="Start address (hex/int)."
)
@click.option(
    "--size",
    required=True,
    type=int,
    help=f"Scan size in bytes (chunked scan, max {MEMORY_FIND_MAX_SCAN_SIZE} bytes).",
)
@click.pass_context
def memory_find(ctx, needle: str, start_addr: str, size: int):
    """Find a UTF-8 needle in memory using a chunked scan."""
    try:
        addr_val = _parse_int(start_addr)
        data = _require_process().find_memory(needle, addr_val, size)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("core")
def core_group():
    """Core dump operations."""


@core_group.command("load")
@click.option("--path", "core_path", required=True, type=click.Path(exists=True))
@click.pass_context
def core_load(ctx, core_path: str):
    """Load a core dump into current target."""
    try:
        data = _require_target().load_core(core_path)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.command("dap")
@click.option(
    "--log-file",
    default=None,
    type=click.Path(dir_okay=False),
    help="Optional file for adapter diagnostics.",
)
@click.option(
    "--profile",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Stop-rule profile JSON.",
)
def dap_server(log_file: str | None, profile: str | None):
    """Run a stdio Debug Adapter Protocol server."""
    from cli_anything.lldb.dap import main as dap_main

    args = []
    if log_file:
        args.extend(["--log-file", log_file])
    if profile:
        args.extend(["--profile", profile])
    dap_main(args)


@cli.group("session")
def session_group():
    """Persistent session lifecycle helpers."""


@session_group.command("info")
@click.pass_context
def session_info(ctx):
    """Show the current persistent session status."""
    try:
        data = _session_status(_get_session())
        data["session_file"] = ctx.obj.get("session_file")
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@session_group.command("close")
@click.pass_context
def session_close(ctx):
    """Close the persistent session and clean up debugger state."""
    try:
        _shutdown_session()
        _output(ctx, {"status": "closed", "session_file": ctx.obj.get("session_file")})
    except Exception as exc:
        _handle_exc(ctx, exc)


def main():
    cli(obj={})
