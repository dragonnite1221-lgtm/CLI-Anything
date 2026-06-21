# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def _load_or_seed_project(project_path: str) -> None:
    """Open an existing project path or seed a new in-memory document for it."""
    sess = get_session()
    if sess.has_project():
        return
    if os.path.exists(project_path):
        proj = doc_mod.open_document(project_path)
    else:
        default_name = os.path.basename(project_path)
        if default_name.endswith(".inkscape-cli.json"):
            default_name = default_name[: -len(".inkscape-cli.json")]
        else:
            default_name = os.path.splitext(default_name)[0]
        default_name = default_name or "untitled"
        proj = doc_mod.create_document(name=default_name)
    sess.set_project(proj, project_path)


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
        except FileNotFoundError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_not_found"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, IndexError, RuntimeError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except FileExistsError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_exists"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def _repl_help(skin=None):
    commands = {
        "document new|open|save|info|profiles|canvas-size|units|json": "Document management",
        "shape add-rect|add-circle|add-ellipse|add-line|add-polygon|add-path|add-star|remove|duplicate|list|get": "Shape operations",
        "text add|set|list": "Text management",
        "style set-fill|set-stroke|set-opacity|set|get|list-properties": "Style properties",
        "transform translate|rotate|scale|skew-x|skew-y|get|clear": "Transform operations",
        "layer add|remove|move-object|set|list|reorder|get": "Layer management",
        "path union|intersection|difference|exclusion|convert|list-operations": "Path boolean operations",
        "gradient add-linear|add-radial|apply|list": "Gradient management",
        "export png|svg|pdf|presets": "Export/render",
        "session status|undo|redo|history": "Session management",
        "help": "Show this help",
        "quit": "Exit REPL",
    }
    if skin is not None:
        skin.help(commands)
    else:
        click.echo("\nCommands:")
        for cmd, desc in commands.items():
            click.echo(f"  {cmd:60s}  {desc}")
        click.echo()


def _auto_save_callback():
    """Auto-save callback that runs after each command."""
    global _auto_save, _session, _dry_run
    if _dry_run:
        return
    if _auto_save and _session and _session.has_project() and _session._modified:
        # Don't auto-save if we're in REPL mode (user can explicitly save)
        if not _repl_mode:
            try:
                saved = _session.save_session()
                click.echo(f"Auto-saved to: {saved}")
            except Exception as e:
                click.echo(f"Auto-save failed: {e}", err=True)
