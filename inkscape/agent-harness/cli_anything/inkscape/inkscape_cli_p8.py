# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli  # noqa: E402,E501
from .inkscape_cli_p7 import session  # noqa: E402,E501
# fmt: on


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


def main():
    cli()
