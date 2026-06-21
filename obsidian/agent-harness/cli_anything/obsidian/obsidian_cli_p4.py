# ruff: noqa: F403, F405, E501
from .obsidian_cli_base import *  # noqa: F403

# fmt: off
from .obsidian_cli_p1 import cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.group()
def session():
    """Session state commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show current session state."""
    data = {
        "host": _host,
        "api_key_set": bool(_api_key),
        "last_path": _last_path or "(none)",
        "json_output": _json_output,
    }
    output(data, "Session Status")


def main():
    cli()
