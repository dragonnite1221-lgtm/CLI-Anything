# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import get_state, handle_iterm2_error, output, save_state_now  # noqa: E402,E501
from .iterm2_ctl_cli_p5 import profile  # noqa: E402,E501
from .iterm2_ctl_cli_p6 import session  # noqa: E402,E501
# fmt: on


@session.command("split")
@click.option("--session-id", default=None)
@click.option(
    "--vertical",
    "-v",
    is_flag=True,
    default=False,
    help="Split vertically (side by side). Default: horizontal.",
)
@click.option(
    "--before",
    is_flag=True,
    default=False,
    help="Insert new pane before the split point.",
)
@click.option("--profile", "-p", default=None)
@click.option("--command", "-c", default=None)
@click.option("--use-as-context", is_flag=True, default=False)
@handle_iterm2_error
def session_split(session_id, vertical, before, profile, command, use_as_context):
    """Split a session into two panes."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(
        sess_mod.split_pane,
        sid,
        vertical=vertical,
        before=before,
        profile=profile,
        command=command,
    )
    if use_as_context:
        state = get_state()
        state.session_id = result.get("new_session_id")
        save_state_now()
    direction = "vertically" if vertical else "horizontally"
    output(result, f"Split {direction}: new session {result['new_session_id']}")


@session.command("close")
@click.argument("session_id", required=False)
@click.option("--force", is_flag=True, default=False)
@handle_iterm2_error
def session_close(session_id, force):
    """Close a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.close_session, sid, force=force)
    output(result, f"Closed session {sid}")


@session.command("activate")
@click.argument("session_id", required=False)
@handle_iterm2_error
def session_activate(session_id):
    """Focus a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.activate_session, sid)
    output(result, f"Activated session {sid}")


@session.command("set-name")
@click.argument("name")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_set_name(name, session_id):
    """Set the display name of a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.set_session_name, sid, name)
    output(result, f"Named session {sid} '{name}'")


@session.command("restart")
@click.option("--session-id", default=None)
@click.option("--only-if-exited", is_flag=True, default=False)
@handle_iterm2_error
def session_restart(session_id, only_if_exited):
    """Restart a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.restart_session, sid, only_if_exited=only_if_exited)
    output(result, f"Restarted session {sid}")


@session.command("get-var")
@click.argument("variable_name")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_get_var(variable_name, session_id):
    """Get a session variable value."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.get_session_variable, sid, variable_name)
    output(result, f"{variable_name} = {result['value']}")


@session.command("set-var")
@click.argument("variable_name")
@click.argument("value")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_set_var(variable_name, value, session_id):
    """Set a session variable."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.set_session_variable, sid, variable_name, value)
    output(result, f"Set {variable_name} = {value}")


@session.command("resize")
@click.option("--session-id", default=None)
@click.option("--columns", "-c", type=int, required=True)
@click.option("--rows", "-r", type=int, required=True)
@handle_iterm2_error
def session_resize(session_id, columns, rows):
    """Resize a session terminal grid."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.set_grid_size, sid, columns, rows)
    output(result, f"Resized session {sid} to {columns}x{rows}")
