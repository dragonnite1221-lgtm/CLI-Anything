# ruff: noqa: F403, F405, E501
from .anygen_cli_base import *  # noqa: F403

# fmt: off
from .anygen_cli_p1 import cli, get_session, output  # noqa: E402,E501
from .anygen_cli_p4 import config  # noqa: E402,E501
# fmt: on


@config.command("delete")
@click.argument("key")
def config_delete(key):
    """Delete a configuration value."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"✓ Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not found in config")


@config.command("path")
def config_path():
    """Show the config file path."""
    from cli_anything.anygen.utils.anygen_backend import CONFIG_FILE

    output({"path": str(CONFIG_FILE)}, f"Config file: {CONFIG_FILE}")


@cli.group()
def session():
    """Session management — history, undo, redo."""
    pass


@session.command("status")
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("history")
@click.option("--limit", "-n", type=int, default=20, help="Max entries")
def session_history(limit):
    """Show command history."""
    sess = get_session()
    entries = sess.history(limit=limit)
    if not entries:
        output([], "No history.")
        return
    output(entries, f"History ({len(entries)} entries):")


@session.command("undo")
def session_undo():
    """Undo last command."""
    sess = get_session()
    entry = sess.undo()
    if entry:
        output(entry.to_dict(), f"✓ Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session.command("redo")
def session_redo():
    """Redo last undone command."""
    sess = get_session()
    entry = sess.redo()
    if entry:
        output(entry.to_dict(), f"✓ Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


def main():
    cli()
