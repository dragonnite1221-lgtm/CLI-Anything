# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import get_state, handle_iterm2_error, output  # noqa: E402,E501
from .iterm2_ctl_cli_p6 import session  # noqa: E402,E501
# fmt: on


@session.command("run-tmux-cmd")
@click.argument("command")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_run_tmux_cmd(command, session_id):
    """Run a tmux command from within a tmux-integrated session.

    The session must be one where `tmux -CC` was started (the "gateway"
    session). Raises if the session is not a tmux integration session.

    Example:
        cli-anything-iterm2 session run-tmux-cmd "rename-window mywork"
        cli-anything-iterm2 session run-tmux-cmd "list-sessions"
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(tmux_mod.run_session_tmux_command, sid, command)
    output(result, f"tmux [{sid}]: {result.get('output', '').strip()}")


@session.command("selection")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_selection(session_id):
    """Get the selected text in a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.get_selection, sid)
    output(result)
    if not _json_output:
        if result["has_selection"]:
            click.echo(result["selected_text"])
        else:
            click.echo("(no selection)")


@session.command("inject")
@click.argument("data")
@click.option("--session-id", default=None)
@click.option(
    "--hex",
    "use_hex",
    is_flag=True,
    default=False,
    help="Interpret DATA as a hex string (e.g. '1b5b41' for ESC[A).",
)
@handle_iterm2_error
def session_inject(data, session_id, use_hex):
    """Inject raw bytes into a session as if received from the shell.

    Useful for sending escape sequences, OSC codes, or other terminal control
    bytes that would normally come from a running program.

    \b
      cli-anything-iterm2 session inject $'\\x1b[2J'      # clear screen (ESC[2J)
      cli-anything-iterm2 session inject "1b5b324a" --hex  # same in hex
      cli-anything-iterm2 session inject $'\\x07'          # bell
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    if use_hex:
        try:
            raw = bytes.fromhex(data)
        except ValueError as e:
            raise click.UsageError(f"Invalid hex string: {e}")
    else:
        raw = data.encode("utf-8", errors="surrogateescape")
    result = run_iterm2(sess_mod.inject_bytes, sid, raw)
    output(result, f"Injected {result['injected_bytes']} byte(s) into session {sid}")


@session.command("get-prompt")
@click.option("--session-id", default=None)
@handle_iterm2_error
def session_get_prompt(session_id):
    """Get the last shell prompt info (requires Shell Integration)."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(prompt_mod.get_last_prompt, sid)
    output(result)
    if not _json_output:
        if result.get("available"):
            click.echo(f"  command: {result.get('command')}")
            click.echo(f"  cwd:     {result.get('working_directory')}")
            click.echo(f"  state:   {result.get('state')}")
        else:
            click.echo("  Shell Integration not available in this session.")


@session.command("wait-prompt")
@click.option("--session-id", default=None)
@click.option(
    "--timeout", "-t", type=float, default=30.0, help="Seconds to wait (default 30)."
)
@handle_iterm2_error
def session_wait_prompt(session_id, timeout):
    """Wait for the next shell prompt (requires Shell Integration).

    Blocks until the shell in the session displays its next prompt, meaning
    the previously running command has completed.
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(prompt_mod.wait_for_prompt, sid, timeout=timeout)
    if result.get("timed_out"):
        output(result, f"Timed out after {timeout}s waiting for prompt.")
    else:
        output(result, f"Prompt received in session {sid}")
