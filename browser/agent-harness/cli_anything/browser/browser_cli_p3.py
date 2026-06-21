# ruff: noqa: F403, F405, E501
from .browser_cli_base import *  # noqa: F403

# fmt: off
from .browser_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .browser_cli_p2 import fs  # noqa: E402,E501
# fmt: on


@fs.command("ls")
@click.argument("path", default="", required=False)
@handle_error
def fs_ls(path):
    """List elements at a path in the accessibility tree."""
    sess = get_session()
    result = fs_mod.list_elements(sess, path)
    if _json_output:
        output(result)
    else:
        entries = result.get("entries", [])
        if not entries:
            click.echo(f"No elements at {path or sess.working_dir}")
            return
        click.echo(f"{'NAME':<40} {'ROLE':<20} {'PATH'}")
        click.echo("─" * 80)
        for entry in entries:
            name = entry.get("name", "")
            role = entry.get("role", "")
            entry_path = entry.get("path", "")
            click.echo(f"{name:<40} {role:<20} {entry_path}")


@fs.command("cd")
@click.argument("path")
@handle_error
def fs_cd(path):
    """Change directory in the accessibility tree."""
    sess = get_session()
    result = fs_mod.change_directory(sess, path)
    if "error" in result:
        output(result, result["error"])
    else:
        output(result, f"Changed to: {sess.working_dir}")


@fs.command("cat")
@click.argument("path", default="", required=False)
@handle_error
def fs_cat(path):
    """Read element content from the accessibility tree."""
    sess = get_session()
    result = fs_mod.read_element(sess, path)
    output(result)


@fs.command("grep")
@click.argument("pattern")
@click.argument("path", default="", required=False)
@handle_error
def fs_grep(pattern, path):
    """Search for pattern in the accessibility tree."""
    sess = get_session()
    result = fs_mod.grep_elements(sess, pattern, path)
    if _json_output:
        output(result)
    else:
        matches = result.get("matches", [])
        if not matches:
            click.echo(f"No matches for '{pattern}'")
            return
        click.echo(f"Matches for '{pattern}':")
        for match in matches:
            click.echo(f"  {match}")


@fs.command("pwd")
@handle_error
def fs_pwd():
    """Print current working directory in accessibility tree."""
    sess = get_session()
    click.echo(sess.working_dir)


@cli.group()
def act():
    """Action commands on elements."""
    pass


@act.command("click")
@click.argument("path")
@handle_error
def act_click(path):
    """Click an element at the given path."""
    sess = get_session()
    use_daemon = sess.daemon_mode
    result = backend.click(path, use_daemon=use_daemon)
    output(result, f"Clicked: {path}")


@act.command("type")
@click.argument("path")
@click.argument("text")
@handle_error
def act_type(path, text):
    """Type text into an input element."""
    sess = get_session()
    use_daemon = sess.daemon_mode
    result = backend.type_text(path, text, use_daemon=use_daemon)
    output(result, f"Typed into: {path}")


@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show current session status."""
    sess = get_session()
    status = sess.status()
    output(status)


@session.command("daemon-start")
@handle_error
def session_daemon_start():
    """Start persistent daemon mode."""
    try:
        backend.start_daemon()
        get_session().enable_daemon()
        output({"daemon": "started"}, "Daemon mode started")
    except RuntimeError as e:
        output({"error": str(e)}, str(e))


@session.command("daemon-stop")
@handle_error
def session_daemon_stop():
    """Stop persistent daemon mode."""
    backend.stop_daemon()
    get_session().disable_daemon()
    output({"daemon": "stopped"}, "Daemon mode stopped")


def main():
    cli()
