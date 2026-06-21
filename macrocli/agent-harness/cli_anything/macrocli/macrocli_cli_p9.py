# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import cli, get_runtime, get_session, handle_error, output  # noqa: E402,E501
from .macrocli_cli_p8 import session  # noqa: E402,E501
# fmt: on


@session.command("status")
@handle_error
def session_status():
    """Show current session status and statistics."""
    sess = get_session()
    data = sess.status()
    output(data, "Session status:")


@session.command("history")
@click.option(
    "--limit", default=10, show_default=True, help="Number of records to show."
)
@handle_error
def session_history(limit):
    """Show recent macro execution history."""
    sess = get_session()
    records = sess.history(limit=limit)

    if _json_output:
        output([r.to_dict() for r in records])
    else:
        if not records:
            click.echo("No runs recorded in this session.")
            return
        click.echo(f"Recent runs ({len(records)}):\n")
        for r in records:
            status = "✓" if r.success else "✗"
            import datetime

            ts = datetime.datetime.fromtimestamp(r.timestamp).strftime("%H:%M:%S")
            click.echo(f"  {status} [{ts}] {r.macro_name}  ({r.duration_ms:.0f}ms)")
            if not r.success:
                click.echo(f"       Error: {r.error}", err=True)


@session.command("save")
@handle_error
def session_save():
    """Persist current session to disk."""
    sess = get_session()
    path = sess.save()
    output({"saved": path, "session_id": sess.session_id}, f"Session saved: {path}")


@session.command("list")
@handle_error
def session_list():
    """List all saved sessions."""
    sessions = ExecutionSession.list_sessions()
    if _json_output:
        output(sessions)
    else:
        if not sessions:
            click.echo("No saved sessions.")
            return
        click.echo("Saved sessions:\n")
        for s in sessions:
            import datetime

            ts = datetime.datetime.fromtimestamp(s.get("timestamp", 0)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            click.echo(f"  {s['session_id']}  ({s['runs']} runs)  {ts}")


@cli.command()
@handle_error
def backends():
    """Show available execution backends and their status."""
    runtime = get_runtime()
    data = runtime.routing.describe()
    if _json_output:
        output(data)
    else:
        click.echo("Execution backends:\n")
        for name, info in sorted(data.items(), key=lambda x: -x[1].get("priority", 0)):
            status = "✓" if info.get("available") else "✗"
            click.echo(
                f"  {status}  {name:<20}  priority={info.get('priority', '?'):<5}"
                f"  available={info.get('available')}"
            )
