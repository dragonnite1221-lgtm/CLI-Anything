# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import get_state, handle_iterm2_error, output  # noqa: E402,E501
from .iterm2_ctl_cli_p6 import session  # noqa: E402,E501
# fmt: on


@session.command("list")
@click.option("--window-id", default=None)
@click.option("--tab-id", default=None)
@handle_iterm2_error
def session_list(window_id, tab_id):
    """List all sessions."""
    wid = window_id or get_state().window_id
    tid = tab_id or get_state().tab_id
    result = run_iterm2(sess_mod.list_sessions, window_id=wid, tab_id=tid)
    output({"sessions": result}, f"{len(result)} session(s)")
    if not _json_output and result:
        for s in result:
            current_mark = " *" if s.get("is_current") else ""
            click.echo(
                f"  {s['session_id']}{current_mark}  "
                f"name={s['name'] or '(unnamed)'}  "
                f"tab={s['tab_id']}"
            )


@session.command("send")
@click.argument("text")
@click.option("--session-id", default=None)
@click.option(
    "--no-newline", is_flag=True, default=False, help="Do not append a newline."
)
@click.option(
    "--suppress-broadcast",
    is_flag=True,
    default=False,
    help="Suppress sending to broadcast domains.",
)
@handle_iterm2_error
def session_send(text, session_id, no_newline, suppress_broadcast):
    """Send text to a session.

    TEXT: The text to send. Use \\n for newlines. A newline is appended
    unless --no-newline is given.

    Example:
        cli-anything-iterm2 session send "ls -la"
        cli-anything-iterm2 session send "pwd" --session-id w0t0p0
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError(
            "No session ID specified. Use --session-id or set context "
            "with 'app current' or 'app set-context'."
        )
    payload = text if no_newline else (text + "\n")
    result = run_iterm2(
        sess_mod.send_text, sid, payload, suppress_broadcast=suppress_broadcast
    )
    output(result, f"Sent {result['text_length']} chars to session {sid}")


@session.command("screen")
@click.option("--session-id", default=None)
@click.option("--lines", "-n", type=int, default=None, help="Max lines to return.")
@handle_iterm2_error
def session_screen(session_id, lines):
    """Get the visible screen contents of a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.get_screen_contents, sid, lines=lines)
    output(result)
    if not _json_output:
        click.echo(
            f"  Session {sid}  ({result['returned_lines']}/{result['total_lines']} lines)"
        )
        click.echo("  " + "─" * 60)
        for line in result["lines"]:
            click.echo(f"  {line}")


@session.command("scrollback")
@click.option("--session-id", default=None)
@click.option(
    "--lines", "-n", type=int, default=None, help="Max lines to return (default: all)."
)
@click.option(
    "--tail",
    "-t",
    type=int,
    default=None,
    help="Return only the last N lines (most recent). Overrides --lines.",
)
@click.option(
    "--strip",
    is_flag=True,
    default=False,
    help="Strip null bytes and non-printable control characters.",
)
@handle_iterm2_error
def session_scrollback(session_id, lines, tail, strip):
    """Get the full scrollback buffer including history beyond the visible screen.

    Unlike 'screen' which only shows the visible terminal area, this reads
    the entire history buffer — everything since the session started (up to
    the scrollback limit).

    \b
      cli-anything-iterm2 session scrollback                  # all history
      cli-anything-iterm2 session scrollback --tail 100       # last 100 lines
      cli-anything-iterm2 session scrollback --lines 500      # first 500 lines
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(sess_mod.get_scrollback, sid, lines=lines, tail=tail)
    if strip:
        import re

        result["lines"] = [
            re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", ln)
            for ln in result["lines"]
        ]
    output(result)
    if not _json_output:
        click.echo(
            f"  Session {sid}  ({result['returned_lines']} lines, "
            f"scrollback={result['scrollback_lines']} screen={result['screen_lines']} "
            f"overflow={result['overflow']})"
        )
        click.echo("  " + "─" * 60)
        for line in result["lines"]:
            click.echo(f"  {line}")
