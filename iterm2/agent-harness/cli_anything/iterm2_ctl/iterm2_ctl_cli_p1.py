# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
# fmt: on


def get_state() -> session_state.SessionState:
    global _state
    if _state is None:
        _state = session_state.load_state()
    return _state


def save_state_now():
    global _state
    if _state is not None:
        session_state.save_state(_state)


def _print_data(data, indent: int = 0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k}:")
                _print_data(v, indent + 1)
            else:
                click.echo(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _print_data(item, indent)
                click.echo(f"{prefix}---")
            else:
                click.echo(f"{prefix}- {item}")
    else:
        click.echo(f"{prefix}{data}")


def output(data, message: str = ""):
    """Print result as JSON (--json) or human-readable."""
    if _json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if data and not message:
            _print_data(data)


def handle_iterm2_error(func):
    """Decorator to format iTerm2 errors nicely."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if _json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        except ValueError as e:
            if _json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    return wrapper


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "use_json",
    is_flag=True,
    default=False,
    help="Output results as JSON (for agent use).",
)
@click.pass_context
def cli(ctx, use_json):
    """cli-anything-iterm2 — Control iTerm2 from the command line.

    Connects to a running iTerm2 instance via the iTerm2 Python API.
    Run without a subcommand to enter the interactive REPL.

    Prerequisites:
      1. iTerm2 must be running
      2. Python API enabled: Preferences → General → Magic → Enable Python API
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# deferred to break import cycle  # noqa: E402
from .iterm2_ctl_cli_p2 import repl  # noqa: E402,E501
