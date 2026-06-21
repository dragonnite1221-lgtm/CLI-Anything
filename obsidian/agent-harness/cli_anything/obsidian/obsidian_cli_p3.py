# ruff: noqa: F403, F405, E501
from .obsidian_cli_base import *  # noqa: F403

# fmt: off
from .obsidian_cli_p1 import _require_api_key, cli, handle_error, output  # noqa: E402,E501
from .obsidian_cli_p2 import vault  # noqa: E402,E501
# fmt: on


@vault.command("append")
@click.argument("path")
@click.option("--content", "-c", required=True, help="Content to append")
@click.option(
    "--position",
    "-p",
    type=click.Choice(["end", "beginning"]),
    default="end",
    help="Insert position (default: end)",
)
@handle_error
def vault_append(path, content, position):
    """Append or prepend content to a note."""
    _require_api_key()
    result = vault_mod.append_note(_host, _api_key, path, content, position=position)
    output(result, f"{'Appended to' if position == 'end' else 'Prepended to'}: {path}")


@cli.group()
def search():
    """Search operations."""
    pass


@search.command("query")
@click.argument("query")
@handle_error
def search_query(query):
    """Search vault using Obsidian's search engine."""
    _require_api_key()
    result = search_mod.search_query(_host, _api_key, query)
    if _json_output:
        output(result)
    else:
        if isinstance(result, list):
            if not result:
                click.echo("No results found.")
                return
            for item in result:
                filename = item.get("filename", "unknown")
                score = item.get("score", "")
                click.echo(f"  {filename}" + (f"  (score: {score})" if score else ""))
        else:
            output(result)


@search.command("simple")
@click.argument("query")
@click.option(
    "--context-length",
    "-l",
    type=int,
    default=100,
    help="Context characters around matches (default: 100)",
)
@handle_error
def search_simple(query, context_length):
    """Simple text search across the vault."""
    _require_api_key()
    result = search_mod.search_simple(
        _host, _api_key, query, context_length=context_length
    )
    if _json_output:
        output(result)
    else:
        if isinstance(result, list):
            if not result:
                click.echo("No results found.")
                return
            for item in result:
                filename = item.get("filename", "unknown")
                matches = item.get("matches", [])
                click.echo(f"  {filename} ({len(matches)} matches)")
                for match in matches[:3]:
                    context = match.get("context", match.get("match", ""))
                    if len(context) > 120:
                        context = context[:120] + "..."
                    click.echo(f"    ...{context}...")
        else:
            output(result)


@cli.group()
def note():
    """Active note operations."""
    pass


@note.command("active")
@handle_error
def note_active():
    """Get the currently active note in Obsidian."""
    _require_api_key()
    result = note_mod.get_active(_host, _api_key)
    if _json_output:
        output(result)
    else:
        click.echo(result.get("content", "(no active note)"))


@note.command("open")
@click.argument("path")
@handle_error
def note_open(path):
    """Open a note in Obsidian."""
    _require_api_key()
    global _last_path
    _last_path = path
    result = note_mod.open_note(_host, _api_key, path)
    output(result, f"Opened: {path}")


@cli.group("command")
def command_group():
    """Obsidian command operations."""
    pass


@command_group.command("list")
@handle_error
def command_list():
    """List available Obsidian commands."""
    _require_api_key()
    result = cmd_mod.list_commands(_host, _api_key)
    if _json_output:
        output(result)
    else:
        commands = result.get("commands", result if isinstance(result, list) else [])
        if not commands:
            click.echo("No commands available.")
            return
        click.echo(f"{'ID':<40} {'NAME'}")
        click.echo("─" * 70)
        for cmd in commands:
            cmd_id = cmd.get("id", "")
            cmd_name = cmd.get("name", "")
            click.echo(f"{cmd_id:<40} {cmd_name}")


@command_group.command("execute")
@click.argument("command_id")
@handle_error
def command_execute(command_id):
    """Execute an Obsidian command by ID."""
    _require_api_key()
    result = cmd_mod.execute_command(_host, _api_key, command_id)
    output(result, f"Executed: {command_id}")


@cli.group()
def server():
    """Server status commands."""
    pass


@server.command("status")
@handle_error
def server_status():
    """Check if Obsidian REST API is running."""
    _require_api_key()
    result = server_mod.server_status(_host, _api_key)
    output(result, f"Obsidian REST API at {_host}: running")
