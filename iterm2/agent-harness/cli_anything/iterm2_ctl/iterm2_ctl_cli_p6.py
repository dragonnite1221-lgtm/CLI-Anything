# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output, save_state_now  # noqa: E402,E501
from .iterm2_ctl_cli_p5 import profile, window  # noqa: E402,E501
# fmt: on


@window.command("fullscreen")
@click.argument("mode", type=click.Choice(["on", "off", "toggle", "status"]))
@click.option("--window-id", default=None)
@handle_iterm2_error
def window_fullscreen(mode, window_id):
    """Control fullscreen mode for a window."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    if mode == "status":
        result = run_iterm2(win_mod.get_window_fullscreen, wid)
        output(result, f"Window {wid} fullscreen: {result['fullscreen']}")
    else:
        if mode == "toggle":
            status = run_iterm2(win_mod.get_window_fullscreen, wid)
            target = not status["fullscreen"]
        else:
            target = mode == "on"
        result = run_iterm2(win_mod.set_window_fullscreen, wid, target)
        output(result, f"Window {wid} fullscreen: {target}")


@cli.group()
def tab():
    """Manage tabs within iTerm2 windows."""


@tab.command("list")
@click.option("--window-id", default=None, help="Filter to specific window.")
@handle_iterm2_error
def tab_list(window_id):
    """List all tabs."""
    wid = window_id or get_state().window_id
    result = run_iterm2(tab_mod.list_tabs, window_id=wid)
    output({"tabs": result}, f"{len(result)} tab(s)")
    if not _json_output and result:
        for t in result:
            current_mark = " *" if t.get("is_current") else ""
            click.echo(
                f"  {t['tab_id']}{current_mark}  "
                f"window={t['window_id']} sessions={t['session_count']}"
            )


@tab.command("create")
@click.option("--window-id", default=None)
@click.option("--profile", "-p", default=None)
@click.option("--command", "-c", default=None)
@click.option("--use-as-context", is_flag=True, default=False)
@handle_iterm2_error
def tab_create(window_id, profile, command, use_as_context):
    """Create a new tab."""
    wid = window_id or get_state().window_id
    result = run_iterm2(
        tab_mod.create_tab, window_id=wid, profile=profile, command=command
    )
    if use_as_context:
        state = get_state()
        state.window_id = result.get("window_id")
        state.tab_id = result.get("tab_id")
        state.session_id = result.get("session_id")
        save_state_now()
    output(result, f"Created tab {result['tab_id']} in window {result['window_id']}")


@tab.command("close")
@click.argument("tab_id", required=False)
@click.option("--force", is_flag=True, default=False)
@handle_iterm2_error
def tab_close(tab_id, force):
    """Close a tab."""
    tid = tab_id or get_state().tab_id
    if not tid:
        raise click.UsageError("No tab ID specified.")
    result = run_iterm2(tab_mod.close_tab, tid, force=force)
    output(result, f"Closed tab {tid}")


@tab.command("activate")
@click.argument("tab_id", required=False)
@handle_iterm2_error
def tab_activate(tab_id):
    """Focus a tab."""
    tid = tab_id or get_state().tab_id
    if not tid:
        raise click.UsageError("No tab ID specified.")
    result = run_iterm2(tab_mod.activate_tab, tid)
    output(result, f"Activated tab {tid}")


@tab.command("info")
@click.argument("tab_id", required=False)
@handle_iterm2_error
def tab_info(tab_id):
    """Get details about a tab."""
    tid = tab_id or get_state().tab_id
    if not tid:
        raise click.UsageError("No tab ID specified.")
    result = run_iterm2(tab_mod.get_tab_info, tid)
    output(result)


@tab.command("select-pane")
@click.argument("direction", type=click.Choice(["left", "right", "above", "below"]))
@click.option("--tab-id", default=None)
@handle_iterm2_error
def tab_select_pane(direction, tab_id):
    """Move focus to the adjacent split pane in a direction.

    DIRECTION: left | right | above | below

    \b
      cli-anything-iterm2 tab select-pane right
      cli-anything-iterm2 tab select-pane below --tab-id <id>
    """
    tid = tab_id or get_state().tab_id
    if not tid:
        raise click.UsageError("No tab ID specified.")
    result = run_iterm2(tab_mod.select_pane_in_direction, tid, direction)
    if result["moved"]:
        output(result, f"Moved focus {direction} → session {result['new_session_id']}")
    else:
        output(result, f"No pane {direction} of current selection.")


@cli.group()
def session():
    """Manage terminal sessions (panes) within iTerm2 tabs."""
