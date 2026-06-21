# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403

# fmt: off
from .qgis_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def get_session() -> Session:
    """Return the process-local session object."""
    global _session
    if _session is None:
        session_dir = Path.home() / ".cli-anything-qgis"
        session_dir.mkdir(parents=True, exist_ok=True)
        _session = Session(str(session_dir / "session.json"))
    return _session


def _print_dict(data: dict, indent: int = 0) -> None:
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            click.echo(f"{prefix}{key}:")
            _print_dict(value, indent + 1)
        elif isinstance(value, list):
            click.echo(f"{prefix}{key}:")
            _print_list(value, indent + 1)
        else:
            click.echo(f"{prefix}{key}: {value}")


def _print_list(items: list, indent: int = 0) -> None:
    prefix = "  " * indent
    for index, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{index}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def output(data, message: str = "") -> None:
    """Emit data in either JSON or human-readable form."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
        return

    if message:
        click.echo(message)
    if isinstance(data, dict):
        _print_dict(data)
    elif isinstance(data, list):
        _print_list(data)
    else:
        click.echo(str(data))


def _error_payload(exc: Exception) -> dict:
    payload = {
        "error": str(exc),
        "type": exc.__class__.__name__,
    }
    if isinstance(exc, QgisProcessError):
        payload["returncode"] = exc.returncode
        if exc.stderr:
            payload["stderr"] = exc.stderr
        if exc.stdout:
            payload["stdout"] = exc.stdout
        if exc.payload:
            payload["payload"] = exc.payload
    return payload


def handle_error(func):
    """Normalize domain/backend errors for CLI and REPL use."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (QgisBackendError, QgisProcessError, ValueError) as exc:
            payload = _error_payload(exc)
            if _json_output:
                click.echo(json.dumps(payload, indent=2, default=str))
            else:
                click.echo(f"Error: {exc}", err=True)
            if not _repl_mode:
                raise SystemExit(1)
            return None

    return wrapper


def _requested_project_path() -> str | None:
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return None
    root = ctx.find_root()
    obj = root.obj or {}
    return obj.get("project_path")


def _current_project_modified() -> bool:
    try:
        return bool(project_mod.current_project().isDirty())
    except Exception:
        return False


def _sync_session_project_path() -> None:
    session = get_session()
    current_path = project_mod.current_project_path()
    if current_path:
        session.set_project_path(current_path)
    else:
        session.clear_project()


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option(
    "--project",
    "project_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Open this project for the current command.",
)
@click.pass_context
def cli(ctx, use_json, project_path):
    """QGIS CLI for project authoring, layout export, and processing."""
    global _json_output
    _json_output = use_json
    get_session()
    ctx.obj = {"project_path": str(project_path) if project_path else None}

    if (
        ctx.invoked_subcommand is None
        and "--help" not in sys.argv
        and "-h" not in sys.argv
    ):
        ctx.invoke(repl)


@cli.group()
def session():
    """Session state and history commands."""
