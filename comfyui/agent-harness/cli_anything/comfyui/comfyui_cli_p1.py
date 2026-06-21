# ruff: noqa: F403, F405, E501
from .comfyui_cli_base import *  # noqa: F403


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def output(data, message: str = ""):
    """Print output in JSON or human-readable format."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def handle_error(func):
    """Decorator for consistent error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(
                    json.dumps(
                        {
                            "error": str(e),
                            "type": type(e).__name__,
                        }
                    )
                )
            else:
                click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option(
    "--url", default=DEFAULT_BASE_URL, show_default=True, help="ComfyUI server URL"
)
@click.pass_context
def cli(ctx, use_json, url):
    """ComfyUI CLI — AI image generation from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output, _base_url
    _json_output = use_json
    _base_url = url

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    click.echo("ComfyUI CLI REPL — type 'help' for commands, 'quit' to exit")
    click.echo(f"Server: {_base_url}")

    try:
        api_get(_base_url, "/system_stats")
        click.echo("Connected to ComfyUI server.")
    except Exception as e:
        click.echo(f"Warning: Could not connect to ComfyUI: {e}", err=True)

    repl_commands = {
        "workflow": "list|load|validate",
        "queue": "prompt|status|clear|history|interrupt",
        "models": "checkpoints|loras|vaes|controlnets|node-info|list-nodes",
        "images": "list|download|download-all",
        "system": "stats|info",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            line = click.prompt(
                "comfyui", prompt_suffix="> ", default="", show_default=False
            )
            line = line.strip()
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                click.echo("Goodbye.")
                break
            if line.lower() == "help":
                for cmd, subs in repl_commands.items():
                    click.echo(f"  {cmd:<12} {subs}")
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
                click.echo(f"Usage error: {e}", err=True)
            except Exception as e:
                click.echo(f"Error: {e}", err=True)

        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye.")
            break


@cli.group()
def workflow():
    """Workflow file management."""
    pass


@workflow.command("list")
@click.argument("directory", default=".", type=click.Path())
@handle_error
def workflow_list(directory):
    """List workflow JSON files in a directory."""
    result = workflow_mod.list_workflows(directory)
    output(result, f"Workflows in {directory}:")
