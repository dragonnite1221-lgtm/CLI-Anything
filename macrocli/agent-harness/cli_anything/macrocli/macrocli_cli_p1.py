# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def get_runtime() -> MacroRuntime:
    global _runtime, _session
    if _runtime is None:
        _session = _session or ExecutionSession()
        _runtime = MacroRuntime(session=_session)
    return _runtime


def get_session() -> ExecutionSession:
    global _session
    if _session is None:
        _session = ExecutionSession()
    return _session


def _print_value(val, indent: int = 0):
    prefix = "  " * indent
    if isinstance(val, dict):
        for k, v in val.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k}:")
                _print_value(v, indent + 1)
            else:
                click.echo(f"{prefix}{k}: {v}")
    elif isinstance(val, list):
        for i, item in enumerate(val):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i}]")
                _print_value(item, indent + 1)
            else:
                click.echo(f"{prefix}- {item}")
    else:
        click.echo(f"{prefix}{val}")


def output(data, message: str = ""):
    """Print result: JSON in --json mode, human-readable otherwise."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _print_value(data)


def handle_error(func):
    """Decorator: consistent error handling across commands."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            msg = str(e).strip("'\"")
            if _json_output:
                click.echo(json.dumps({"error": msg, "type": "not_found"}))
            else:
                click.echo(f"Error: {msg}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except FileNotFoundError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_not_found"}))
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

    return wrapper


def _parse_params(param_tuples: tuple) -> dict:
    """Convert --param key=value tuples to a dict."""
    result = {}
    for pair in param_tuples:
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            click.echo(
                f"Warning: --param '{pair}' ignored (expected key=value format).",
                err=True,
            )
    return result


@click.group(invoke_without_command=True)
@click.option("--json", "json_flag", is_flag=True, help="Machine-readable JSON output.")
@click.option(
    "--dry-run",
    "dry_run_flag",
    is_flag=True,
    help="Simulate execution without side effects.",
)
@click.option("--session-id", default=None, help="Resume or create a named session.")
@click.pass_context
def cli(ctx, json_flag, dry_run_flag, session_id):
    """MacroCLI — run GUI workflows as CLI commands.

    \b
    Quick start:
      cli-anything-macrocli macro list
      cli-anything-macrocli macro info <name>
      cli-anything-macrocli macro run <name> --param key=value

    Enter interactive REPL by running without arguments.
    """
    global _json_output, _dry_run, _session

    _json_output = json_flag
    _dry_run = dry_run_flag

    if session_id:
        loaded = ExecutionSession.load(session_id)
        _session = loaded or ExecutionSession(session_id=session_id)

    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
