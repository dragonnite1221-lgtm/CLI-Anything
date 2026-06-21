# ruff: noqa: F403, F405, E501
from .obsidian_cli_base import *  # noqa: F403

# fmt: off
from .obsidian_cli_p1 import _require_api_key, cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.obsidian.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("obsidian", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "vault": "list|read|create|update|delete|append",
        "search": "query|simple",
        "note": "active|open",
        "command": "list|execute",
        "server": "status",
        "session": "status",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            context = _last_path if _last_path else ""
            line = skin.get_input(pt_session, project_name=context, modified=False)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


@cli.group()
def vault():
    """Vault file operations."""
    pass


@vault.command("list")
@click.argument("path", default="/")
@handle_error
def vault_list(path):
    """List files and folders in the vault."""
    _require_api_key()
    result = vault_mod.list_files(_host, _api_key, path)
    files = result.get("files", [])
    if _json_output:
        output(result)
    else:
        if not files:
            click.echo("No files found.")
            return
        click.echo(f"{'FILE':<60}")
        click.echo("─" * 60)
        for f in files:
            click.echo(f"{f}")


@vault.command("read")
@click.argument("path")
@handle_error
def vault_read(path):
    """Read a note's content."""
    _require_api_key()
    global _last_path
    _last_path = path
    result = vault_mod.read_note(_host, _api_key, path)
    if _json_output:
        output(result)
    else:
        click.echo(result.get("content", ""))


@vault.command("create")
@click.argument("path")
@click.option("--content", "-c", default="", help="Note content (markdown)")
@click.option(
    "--file",
    "-f",
    "input_file",
    type=click.Path(exists=True),
    help="Read content from file",
)
@handle_error
def vault_create(path, content, input_file):
    """Create a new note in the vault."""
    _require_api_key()
    if input_file:
        with open(input_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    result = vault_mod.create_note(_host, _api_key, path, content)
    output(result, f"Created: {path}")


@vault.command("update")
@click.argument("path")
@click.option("--content", "-c", default="", help="New note content (markdown)")
@click.option(
    "--file",
    "-f",
    "input_file",
    type=click.Path(exists=True),
    help="Read content from file",
)
@handle_error
def vault_update(path, content, input_file):
    """Update an existing note (overwrites content)."""
    _require_api_key()
    if input_file:
        with open(input_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    result = vault_mod.update_note(_host, _api_key, path, content)
    output(result, f"Updated: {path}")


@vault.command("delete")
@click.argument("path")
@handle_error
def vault_delete(path):
    """Delete a note from the vault."""
    _require_api_key()
    result = vault_mod.delete_note(_host, _api_key, path)
    output(result, f"Deleted: {path}")
