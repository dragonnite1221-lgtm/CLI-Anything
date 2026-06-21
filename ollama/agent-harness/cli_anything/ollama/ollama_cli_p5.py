# ruff: noqa: F403, F405, E501
from .ollama_cli_base import *  # noqa: F403

# fmt: off
from .ollama_cli_p1 import cli, handle_error, output  # noqa: E402,E501
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
        "last_model": _last_model or "(none)",
        "chat_history_length": len(_chat_history),
        "json_output": _json_output,
    }
    output(data, "Session Status")


@session.command("history")
@handle_error
def session_history():
    """Show chat history for current session."""
    if not _chat_history:
        output({"messages": []}, "No chat history.")
        return
    if _json_output:
        output({"messages": _chat_history})
    else:
        for msg in _chat_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            # Truncate long messages for display
            if len(content) > 200:
                content = content[:200] + "..."
            click.echo(f"[{role}] {content}")


def main():
    cli()
