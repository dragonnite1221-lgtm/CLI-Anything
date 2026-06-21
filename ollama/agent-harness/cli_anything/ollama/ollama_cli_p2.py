# ruff: noqa: F403, F405, E501
from .ollama_cli_base import *  # noqa: F403

# fmt: off
from .ollama_cli_p1 import cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.ollama.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("ollama", version="1.0.1")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "model": "list|show|pull|rm|copy|ps",
        "generate": "text|chat",
        "embed": "text",
        "server": "status|version",
        "session": "status|history",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            context = _last_model if _last_model else ""
            line = skin.get_input(pt_session, project_name=context, modified=False)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            # Parse and execute command (shlex handles quoted strings with spaces)
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
def model():
    """Model management commands."""
    pass


def _format_size(size_bytes: int) -> str:
    """Format byte count as human-readable string."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


@model.command("list")
@handle_error
def model_list():
    """List locally available models."""
    result = models_mod.list_models(_host)
    models = result.get("models", [])
    if _json_output:
        output(result)
    else:
        if not models:
            click.echo("No models installed. Pull one with: model pull <name>")
            return
        click.echo(f"{'NAME':<40} {'SIZE':<12} {'MODIFIED'}")
        click.echo("─" * 70)
        for m in models:
            name = m.get("name", "")
            size = m.get("size", 0)
            modified = m.get("modified_at", "")[:19]
            size_str = _format_size(size)
            click.echo(f"{name:<40} {size_str:<12} {modified}")


@model.command("show")
@click.argument("name")
@handle_error
def model_show(name):
    """Show model details (parameters, template, license)."""
    result = models_mod.show_model(_host, name)
    output(result, f"Model: {name}")
