# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output, save_state_now  # noqa: E402,E501
# fmt: on


@cli.group()
def tmux():
    """Manage iTerm2 tmux integration connections.

    Requires at least one active `tmux -CC` session running inside iTerm2.
    Start one with:  tmux -CC          (new session)
                     tmux -CC attach   (attach to existing)
    """


@tmux.command("list")
@handle_iterm2_error
def tmux_list():
    """List all active tmux integration connections."""
    result = run_iterm2(tmux_mod.list_connections)
    output(
        {"connections": result},
        f"{len(result)} tmux connection(s)"
        if result
        else "No active tmux connections.",
    )
    if not _json_output and result:
        for c in result:
            click.echo(
                f"  {c['connection_id']}  gateway-session={c['owning_session_id']}"
            )


@tmux.command("send")
@click.argument("command")
@click.option(
    "--connection-id",
    default=None,
    help="Tmux connection ID (default: first available).",
)
@handle_iterm2_error
def tmux_send(command, connection_id):
    """Send a tmux command to an active connection.

    COMMAND is any valid tmux command, e.g.:

    \b
      cli-anything-iterm2 tmux send "list-sessions"
      cli-anything-iterm2 tmux send "new-window -n work"
      cli-anything-iterm2 tmux send "rename-session dev"
      cli-anything-iterm2 tmux send "split-window -h"
    """
    result = run_iterm2(tmux_mod.send_command, command, connection_id=connection_id)
    output(result, result.get("output", "").strip() or "(no output)")


@tmux.command("create-window")
@click.option(
    "--connection-id",
    default=None,
    help="Tmux connection ID (default: first available).",
)
@click.option(
    "--use-as-context",
    is_flag=True,
    default=False,
    help="Save new window/session as the current context.",
)
@handle_iterm2_error
def tmux_create_window(connection_id, use_as_context):
    """Create a new tmux window (surfaces as an iTerm2 tab)."""
    result = run_iterm2(tmux_mod.create_window, connection_id=connection_id)
    if use_as_context:
        state = get_state()
        state.window_id = result.get("window_id")
        state.tab_id = result.get("tab_id")
        state.session_id = result.get("session_id")
        save_state_now()
    output(
        result,
        f"Created tmux window: tab={result.get('tab_id')} "
        f"session={result.get('session_id')}",
    )


@tmux.command("set-visible")
@click.argument("tmux_window_id")
@click.argument("mode", type=click.Choice(["on", "off"]))
@click.option("--connection-id", default=None)
@handle_iterm2_error
def tmux_set_visible(tmux_window_id, mode, connection_id):
    """Show or hide a tmux window tab.

    TMUX_WINDOW_ID is the tmux window ID (e.g. @1). Get it from `tmux tabs`.

    \b
      cli-anything-iterm2 tmux set-visible @1 off   # hide
      cli-anything-iterm2 tmux set-visible @1 on    # show
    """
    visible = mode == "on"
    result = run_iterm2(
        tmux_mod.set_window_visible,
        tmux_window_id,
        visible,
        connection_id=connection_id,
    )
    state_str = "visible" if visible else "hidden"
    output(result, f"Tmux window {tmux_window_id} is now {state_str}")


@tmux.command("tabs")
@handle_iterm2_error
def tmux_tabs():
    """List all iTerm2 tabs backed by a tmux integration window."""
    result = run_iterm2(tmux_mod.list_tmux_tabs)
    output(
        {"tmux_tabs": result},
        f"{len(result)} tmux tab(s)" if result else "No tmux-backed tabs found.",
    )
    if not _json_output and result:
        for t in result:
            click.echo(
                f"  tab={t['tab_id']}  tmux-window={t['tmux_window_id']}  "
                f"connection={t['tmux_connection_id']}"
            )


@tmux.command("bootstrap")
@click.option(
    "--attach",
    is_flag=True,
    default=False,
    help="Run `tmux -CC attach` instead of `tmux -CC`.",
)
@click.option(
    "--session-id",
    default=None,
    help="Session to send the command to (default: first session).",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=15.0,
    help="Seconds to wait for connection to appear (default 15).",
)
@handle_iterm2_error
def tmux_bootstrap(attach, session_id, timeout):
    """Start a tmux -CC session and wait for the integration to connect.

    Sends `tmux -CC` (or `tmux -CC attach` with --attach) to a terminal
    session, then polls until the iTerm2 tmux integration connection appears.

    \b
      cli-anything-iterm2 tmux bootstrap                # start new session
      cli-anything-iterm2 tmux bootstrap --attach       # attach to existing
      cli-anything-iterm2 tmux bootstrap --session-id w0t0p0
    """
    sid = session_id or get_state().session_id
    result = run_iterm2(
        tmux_mod.bootstrap, attach=attach, session_id=sid, timeout=timeout
    )
    output(
        result,
        f"tmux -CC connected: {result['connection_id']} ({result['elapsed_seconds']}s)",
    )
