# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403


_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_auto_save = False
_dry_run = False
def _print_dict(d: dict, indent: int = 2):
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{' ' * indent}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{' ' * indent}{k}: [{len(v)} items]")
        else:
            click.echo(f"{' ' * indent}{k}: {v}")
def _print_list(items: list):
    if not items:
        click.echo("  (empty)")
        return
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"  [{i}]")
            _print_dict(item, indent=4)
        else:
            click.echo(f"  [{i}] {item}")
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
    """Decorator to catch and format errors."""
    @functools.wraps(func)
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
        except (ValueError, IndexError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "validation"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except RuntimeError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "runtime"}))
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
    return wrapper
def _repl_zoom(args, skin, pt_session=None):
    """Handle zoom subcommands in REPL."""
    if not args:
        skin.error("Usage: zoom list|add|rm <id>")
        return
    sub = args[0]
    if sub == "list":
        result = tl_mod.list_zoom_regions(_session)
        output(result)
    elif sub == "add":
        skin.info("Add zoom region:")
        start = int(skin.sub_input("  start_ms: ", pt_session))
        end = int(skin.sub_input("  end_ms: ", pt_session))
        depth = int(skin.sub_input("  depth (1-6, default 3): ", pt_session) or "3")
        fx = float(skin.sub_input("  focus_x (0-1, default 0.5): ", pt_session) or "0.5")
        fy = float(skin.sub_input("  focus_y (0-1, default 0.5): ", pt_session) or "0.5")
        result = tl_mod.add_zoom_region(_session, start, end, depth, fx, fy)
        skin.success(f"Added zoom: {result['id']}")
    elif sub == "rm" and len(args) > 1:
        tl_mod.remove_zoom_region(_session, args[1])
        skin.success(f"Removed: {args[1]}")
    else:
        skin.error("Usage: zoom list|add|rm <id>")
def _repl_speed(args, skin, pt_session=None):
    """Handle speed subcommands in REPL."""
    if not args:
        skin.error("Usage: speed list|add|rm <id>")
        return
    sub = args[0]
    if sub == "list":
        result = tl_mod.list_speed_regions(_session)
        output(result)
    elif sub == "add":
        skin.info("Add speed region:")
        start = int(skin.sub_input("  start_ms: ", pt_session))
        end = int(skin.sub_input("  end_ms: ", pt_session))
        spd = float(skin.sub_input("  speed (0.25-2.0, default 1.5): ", pt_session) or "1.5")
        result = tl_mod.add_speed_region(_session, start, end, spd)
        skin.success(f"Added speed: {result['id']}")
    elif sub == "rm" and len(args) > 1:
        tl_mod.remove_speed_region(_session, args[1])
        skin.success(f"Removed: {args[1]}")
    else:
        skin.error("Usage: speed list|add|rm <id>")
