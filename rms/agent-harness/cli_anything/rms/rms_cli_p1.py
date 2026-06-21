# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def _get_session():
    global _session
    if _session is None:
        sf = str(Path.home() / ".cli-anything-rms" / "session.json")
        _session = Session(session_file=sf)
    return _session


def _get_token():
    return _token or get_api_token()


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
    @functools.wraps(func)
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

    return wrapper


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--token", "token_opt", type=str, default=None, help="RMS API token")
@click.pass_context
def cli(ctx, use_json, token_opt):
    """Teltonika RMS CLI — manage devices, alerts, and more."""
    global _json_output, _token
    _json_output = use_json
    _token = token_opt
    ctx.ensure_object(dict)
    ctx.obj["token"] = token_opt

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
