# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output, save_state_now  # noqa: E402,E501
# fmt: on


@cli.group()
def window():
    """Manage iTerm2 windows."""


@window.command("list")
@handle_iterm2_error
def window_list():
    """List all open windows."""
    result = run_iterm2(win_mod.list_windows)
    output(
        {"windows": result},
        f"{len(result)} window(s)" if result else "No windows open.",
    )
    if not _json_output and result:
        for w in result:
            current_mark = " *" if w.get("is_current") else ""
            click.echo(
                f"  {w['window_id']}{current_mark}  "
                f"tabs={w['tab_count']} sessions={w['session_count']}"
            )


@cli.group()
def profile():
    """Manage iTerm2 profiles."""


@window.command("create")
@click.option("--profile", "-p", default=None, help="Profile name.")
@click.option("--command", "-c", default=None, help="Command to run.")
@click.option(
    "--use-as-context",
    is_flag=True,
    default=False,
    help="Save new window/tab/session as the current context.",
)
@handle_iterm2_error
def window_create(profile, command, use_as_context):
    """Create a new iTerm2 window."""
    result = run_iterm2(win_mod.create_window, profile=profile, command=command)
    if use_as_context:
        state = get_state()
        state.window_id = result.get("window_id")
        state.tab_id = result.get("tab_id")
        state.session_id = result.get("session_id")
        save_state_now()
    output(result, f"Created window {result['window_id']}")


@window.command("close")
@click.argument("window_id", required=False)
@click.option(
    "--force", is_flag=True, default=False, help="Force close without confirmation."
)
@handle_iterm2_error
def window_close(window_id, force):
    """Close a window. Uses context window if WINDOW_ID is omitted."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError(
            "No window ID specified and no context window set. "
            "Use 'app current' or 'app set-context' first."
        )
    result = run_iterm2(win_mod.close_window, wid, force=force)
    output(result, f"Closed window {wid}")


@window.command("activate")
@click.argument("window_id", required=False)
@handle_iterm2_error
def window_activate(window_id):
    """Bring a window to the foreground."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    result = run_iterm2(win_mod.activate_window, wid)
    output(result, f"Activated window {wid}")


@window.command("set-title")
@click.argument("title")
@click.option("--window-id", default=None)
@handle_iterm2_error
def window_set_title(title, window_id):
    """Set the title of a window."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    result = run_iterm2(win_mod.set_window_title, wid, title)
    output(result, f"Set title of {wid} to '{title}'")


@window.command("frame")
@click.option("--window-id", default=None)
@handle_iterm2_error
def window_frame(window_id):
    """Get the position and size of a window."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    result = run_iterm2(win_mod.get_window_frame, wid)
    output(
        result,
        f"Window {wid}: x={result['x']} y={result['y']} "
        f"w={result['width']} h={result['height']}",
    )


@window.command("set-frame")
@click.option("--window-id", default=None)
@click.option("--x", type=float, required=True)
@click.option("--y", type=float, required=True)
@click.option("--width", type=float, required=True)
@click.option("--height", type=float, required=True)
@handle_iterm2_error
def window_set_frame(window_id, x, y, width, height):
    """Set the position and size of a window."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    result = run_iterm2(win_mod.set_window_frame, wid, x, y, width, height)
    output(result, f"Moved window {wid} to ({x},{y}) size {width}x{height}")
