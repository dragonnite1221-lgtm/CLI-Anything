"""Element-action command registration for the browser CLI."""

from __future__ import annotations

import click


def register_act_commands(root, get_session, output, handle_error, backend) -> None:
    """Attach click and type actions to the root command group."""

    @root.group()
    def act():
        """Action commands on elements."""

    @act.command("click")
    @click.argument("path")
    @handle_error
    def act_click(path):
        """Click an element at the given path."""

        result = backend.click(path, use_daemon=get_session().daemon_mode)
        output(result, f"Clicked: {path}")

    @act.command("type")
    @click.argument("path")
    @click.argument("text")
    @handle_error
    def act_type(path, text):
        """Type text into an input element."""

        result = backend.type_text(path, text, use_daemon=get_session().daemon_mode)
        output(result, f"Typed into: {path}")
