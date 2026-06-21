# ruff: noqa: F403, F405, E501
from .novita_cli_base import *  # noqa: F403

# fmt: off
from .novita_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def get_session():
    global _session
    if _session is None:
        sf = str(Path.home() / ".cli-anything-novita" / "session.json")
        _session = ChatSession(session_file=sf)
    return _session


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
        else:
            click.echo(str(data))


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--api-key", "api_key_opt", type=str, default=None, help="Novita API key")
@click.option(
    "--model",
    "model_opt",
    type=str,
    default=None,
    help="Model ID (default: deepseek/deepseek-v3.2)",
)
@click.pass_context
def cli(ctx, use_json, api_key_opt, model_opt):
    """Novita CLI — OpenAI-compatible AI API client."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key_opt
    ctx.obj["model"] = model_opt

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
