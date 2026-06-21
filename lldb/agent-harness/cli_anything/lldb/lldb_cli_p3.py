# ruff: noqa: F403, F405, E501
from .lldb_cli_base import *  # noqa: F403

# fmt: off
from .lldb_cli_p1 import _handle_exc, _output, _require_process, _require_target, cli  # noqa: E402,E501
from .lldb_cli_p2 import process_group  # noqa: E402,E501
# fmt: on


@process_group.command("attach")
@click.option("--pid", type=int, default=None, help="Attach by process ID.")
@click.option("--name", type=str, default=None, help="Attach by process name.")
@click.option(
    "--wait-for", is_flag=True, help="Wait for process launch when attaching by name."
)
@click.pass_context
def process_attach(ctx, pid, name, wait_for):
    """Attach to existing process."""
    try:
        s = _require_target()
        if pid is not None:
            data = s.attach_pid(pid)
        elif name:
            data = s.attach_name(name, wait_for=wait_for)
        else:
            raise click.ClickException("Specify --pid or --name")
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@process_group.command("continue")
@click.pass_context
def process_continue(ctx):
    """Continue execution."""
    try:
        data = _require_process().continue_exec()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@process_group.command("interrupt")
@click.pass_context
def process_interrupt(ctx):
    """Interrupt a running process."""
    try:
        data = _require_process().interrupt()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@process_group.command("detach")
@click.pass_context
def process_detach(ctx):
    """Detach from process."""
    try:
        data = _require_process().detach()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@process_group.command("info")
@click.pass_context
def process_info(ctx):
    """Show process status."""
    try:
        data = _require_process().process_info()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("breakpoint")
def breakpoint_group():
    """Breakpoint operations."""


@breakpoint_group.command("set")
@click.option("--file", "file_path", type=str, default=None)
@click.option("--line", type=int, default=None)
@click.option("--function", type=str, default=None)
@click.option("--condition", type=str, default=None)
@click.option(
    "--allow-pending", is_flag=True, help="Allow unresolved pending breakpoints."
)
@click.pass_context
def breakpoint_set(ctx, file_path, line, function, condition, allow_pending):
    """Set a breakpoint by file/line or function."""
    try:
        data = _require_target().breakpoint_set(
            file=file_path,
            line=line,
            function=function,
            condition=condition,
            allow_pending=allow_pending,
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@breakpoint_group.command("list")
@click.pass_context
def breakpoint_list(ctx):
    """List breakpoints."""
    try:
        data = _require_target().breakpoint_list()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@breakpoint_group.command("delete")
@click.option("--id", "bp_id", required=True, type=int)
@click.pass_context
def breakpoint_delete(ctx, bp_id: int):
    """Delete breakpoint by ID."""
    try:
        data = _require_target().breakpoint_delete(bp_id)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@breakpoint_group.command("enable")
@click.option("--id", "bp_id", required=True, type=int)
@click.pass_context
def breakpoint_enable(ctx, bp_id: int):
    """Enable breakpoint."""
    try:
        data = _require_target().breakpoint_enable(bp_id, enabled=True)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@breakpoint_group.command("disable")
@click.option("--id", "bp_id", required=True, type=int)
@click.pass_context
def breakpoint_disable(ctx, bp_id: int):
    """Disable breakpoint."""
    try:
        data = _require_target().breakpoint_enable(bp_id, enabled=False)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("thread")
def thread_group():
    """Thread operations."""


@thread_group.command("list")
@click.pass_context
def thread_list(ctx):
    """List threads."""
    try:
        data = _require_process().threads()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)
