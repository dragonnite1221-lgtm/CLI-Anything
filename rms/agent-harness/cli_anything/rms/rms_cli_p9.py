# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_session, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p8 import session_group  # noqa: E402,E501
# fmt: on


@session_group.command("history")
@click.option("--limit", "-n", type=int, default=20)
@handle_error
def session_history(limit):
    """Show command history."""
    s = _get_session()
    history = s.history[-limit:]
    output(history, f"History ({len(history)} entries)")


def main():
    cli()
