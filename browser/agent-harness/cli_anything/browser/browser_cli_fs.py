"""Accessibility-tree filesystem command registration for the browser CLI."""

from __future__ import annotations

import click

from cli_anything.browser.core import fs as fs_mod


def register_fs_commands(root, get_session, output, handle_error, is_json_output) -> None:
    """Attach filesystem commands while reading JSON mode from the root CLI."""

    @root.group()
    def fs():
        """Filesystem navigation commands (Accessibility Tree)."""

    @fs.command("ls")
    @click.argument("path", default="", required=False)
    @handle_error
    def fs_ls(path):
        """List elements at a path in the accessibility tree."""

        session = get_session()
        result = fs_mod.list_elements(session, path)
        if is_json_output():
            output(result)
            return
        entries = result.get("entries", [])
        if not entries:
            click.echo(f"No elements at {path or session.working_dir}")
            return
        click.echo(f"{'NAME':<40} {'ROLE':<20} {'PATH'}")
        click.echo("─" * 80)
        for entry in entries:
            click.echo(f"{entry.get('name', ''):<40} {entry.get('role', ''):<20} {entry.get('path', '')}")

    @fs.command("cd")
    @click.argument("path")
    @handle_error
    def fs_cd(path):
        """Change directory in the accessibility tree."""

        session = get_session()
        result = fs_mod.change_directory(session, path)
        output(result, result.get("error", f"Changed to: {session.working_dir}"))

    @fs.command("cat")
    @click.argument("path", default="", required=False)
    @handle_error
    def fs_cat(path):
        """Read element content from the accessibility tree."""

        output(fs_mod.read_element(get_session(), path))

    @fs.command("grep")
    @click.argument("pattern")
    @click.argument("path", default="", required=False)
    @handle_error
    def fs_grep(pattern, path):
        """Search for a pattern in the accessibility tree."""

        result = fs_mod.grep_elements(get_session(), pattern, path)
        if is_json_output():
            output(result)
            return
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
        """Print the current accessibility-tree working directory."""

        click.echo(get_session().working_dir)
