# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403


def get_session() -> Session:
    """Get or create the global session."""
    global _session
    if _session is None:
        _session = Session()
    return _session


def _print_dict(d: dict, indent: int = 0):
    """Pretty-print a dict."""
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
    """Pretty-print a list."""
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def output(data, message: str = ""):
    """Output result data. JSON mode or human-readable."""
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
    """Decorator to handle errors consistently."""

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
        except FileExistsError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_exists"}))
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
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "unexpected"}))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


REPL_COMMANDS = {
    "help": "Show this help",
    "status": "Show session status",
    "new [preset]": "Create new diagram (letter, a4, 16:9, ...)",
    "open <path>": "Open a .drawio file",
    "save [path]": "Save the project",
    "info": "Show project info",
    "xml": "Print raw XML",
    "add <type> [label]": "Add shape (rectangle, ellipse, diamond, ...)",
    "remove <id>": "Remove a shape or connector",
    "shapes": "List all shapes",
    "label <id> <text>": "Update shape label",
    "move <id> <x> <y>": "Move a shape",
    "resize <id> <w> <h>": "Resize a shape",
    "style <id> <key> <val>": "Set style property",
    "connect <src> <tgt> [style]": "Add connector",
    "connectors": "List all connectors",
    "pages": "List all pages",
    "addpage [name]": "Add a new page",
    "export <path> [format]": "Export diagram (png, pdf, svg)",
    "undo": "Undo last operation",
    "redo": "Redo last undone operation",
    "quit": "Exit the REPL",
}
