# ruff: noqa: F403, F405, E501
from .lldb_cli_base import *  # noqa: F403

# fmt: off
from .lldb_cli_p1 import _handle_exc, _output, _parse_int, _require_process, cli  # noqa: E402,E501
from .lldb_cli_p3 import thread_group  # noqa: E402,E501
# fmt: on


@thread_group.command("select")
@click.option("--id", "thread_id", required=True, type=int)
@click.pass_context
def thread_select(ctx, thread_id: int):
    """Select thread."""
    try:
        data = _require_process().thread_select(thread_id)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@thread_group.command("backtrace")
@click.option("--limit", type=int, default=50, show_default=True)
@click.pass_context
def thread_backtrace(ctx, limit: int):
    """Show backtrace of selected thread."""
    try:
        data = _require_process().backtrace(limit=limit)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@thread_group.command("info")
@click.pass_context
def thread_info(ctx):
    """Show selected thread info."""
    try:
        threads = _require_process().threads().get("threads", [])
        selected = next((t for t in threads if t.get("selected")), None)
        if selected is None:
            raise RuntimeError("No selected thread")
        _output(ctx, selected)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("frame")
def frame_group():
    """Frame operations."""


@frame_group.command("select")
@click.option("--index", required=True, type=int)
@click.pass_context
def frame_select(ctx, index: int):
    """Select frame by index in selected thread."""
    try:
        data = _require_process().frame_select(index)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@frame_group.command("info")
@click.pass_context
def frame_info(ctx):
    """Show selected frame info."""
    try:
        data = _require_process().frame_info()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@frame_group.command("locals")
@click.pass_context
def frame_locals(ctx):
    """List local variables in selected frame."""
    try:
        data = _require_process().locals()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("step")
def step_group():
    """Single-step execution commands."""


@step_group.command("over")
@click.pass_context
def step_over(ctx):
    """Step over."""
    try:
        data = _require_process().step_over()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@step_group.command("into")
@click.pass_context
def step_into(ctx):
    """Step into."""
    try:
        data = _require_process().step_into()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@step_group.command("out")
@click.pass_context
def step_out(ctx):
    """Step out."""
    try:
        data = _require_process().step_out()
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.command("expr")
@click.argument("expression", nargs=-1, required=True)
@click.pass_context
def expr_eval(ctx, expression):
    """Evaluate expression in selected frame."""
    try:
        expr = " ".join(expression)
        data = _require_process().evaluate(expr)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("memory")
def memory_group():
    """Memory inspection."""


@memory_group.command("read")
@click.option(
    "--address", required=True, type=str, help="Address, supports hex (e.g. 0x1000)."
)
@click.option("--size", required=True, type=int, help="Number of bytes to read.")
@click.pass_context
def memory_read(ctx, address: str, size: int):
    """Read process memory."""
    try:
        addr_val = _parse_int(address)
        data = _require_process().read_memory(addr_val, size)
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)
