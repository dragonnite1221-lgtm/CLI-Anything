# ruff: noqa: F403, F405, E501
from .obsidian_cli_base import *  # noqa: F403

# fmt: off
from .obsidian_cli_p2 import repl  # noqa: E402,E501
# fmt: on


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
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "runtime_error"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, IndexError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def _require_api_key():
    """Check that API key is set, raise error if not."""
    if not _api_key:
        raise RuntimeError(
            "API key required. Use --api-key or set OBSIDIAN_API_KEY env var."
        )


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option(
    "--host",
    type=str,
    default=None,
    help=f"Obsidian REST API URL (default: {DEFAULT_BASE_URL})",
)
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="API key for authentication (or set OBSIDIAN_API_KEY env var)",
)
@click.pass_context
def cli(ctx, use_json, host, api_key):
    """Obsidian CLI — Knowledge management and note-taking.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output, _host, _api_key
    _json_output = use_json
    _host = host if host else DEFAULT_BASE_URL
    _api_key = api_key or os.environ.get("OBSIDIAN_API_KEY", "")

    if ctx.invoked_subcommand is None:
        _require_api_key()
        ctx.invoke(repl)
