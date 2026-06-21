# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403

# fmt: off
from .krita_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def _output(data: dict, ctx: click.Context) -> None:
    """Print output as JSON or human-readable based on --json flag."""
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        for key, val in data.items():
            click.echo(f"  {key}: {val}")


def handle_error(func):
    """Decorator for consistent error handling across commands."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as exc:
            ctx = click.get_current_context()
            if ctx.obj.get("json"):
                click.echo(json.dumps({"error": str(exc), "type": "FileNotFoundError"}))
            else:
                click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)
        except FileExistsError as exc:
            ctx = click.get_current_context()
            if ctx.obj.get("json"):
                click.echo(json.dumps({"error": str(exc), "type": "FileExistsError"}))
            else:
                click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)
        except RuntimeError as exc:
            ctx = click.get_current_context()
            if ctx.obj.get("json"):
                click.echo(json.dumps({"error": str(exc), "type": "RuntimeError"}))
            else:
                click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)
        except Exception as exc:
            ctx = click.get_current_context()
            if ctx.obj.get("json"):
                click.echo(json.dumps({"error": str(exc), "type": type(exc).__name__}))
            else:
                click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)

    return wrapper


def _load_project(ctx: click.Context) -> dict:
    """Load the current project, from --project flag or global state."""
    global _current_project, _current_project_path
    project_path = ctx.obj.get("project")
    if project_path:
        _current_project = open_project(project_path)
        _current_project_path = project_path
    if _current_project is None:
        raise RuntimeError(
            "No project loaded. Use 'project new' or 'project open' first, or pass --project."
        )
    return _current_project


def _save_current(ctx: click.Context) -> None:
    """Save the current project if a path is known."""
    global _current_project, _current_project_path
    if _current_project and _current_project_path:
        save_project(_current_project, _current_project_path)


@click.group(invoke_without_command=True)
@click.option(
    "--json", "use_json", is_flag=True, default=False, help="Output in JSON format."
)
@click.option(
    "--project",
    "-p",
    type=click.Path(),
    default=None,
    help="Path to project JSON file.",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="Run command without saving changes to disk",
)
@click.pass_context
def cli(ctx, use_json, project, dry_run):
    """cli-anything-krita: CLI harness for Krita digital painting."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json
    ctx.obj["project"] = project

    # Auto-save after one-shot commands when --project is used
    is_oneshot = ctx.invoked_subcommand is not None

    @ctx.call_on_close
    def _auto_save():
        if dry_run or not is_oneshot:
            return
        if _current_project and _current_project_path:
            save_project(_current_project, _current_project_path)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project)


@cli.group()
@click.pass_context
def project(ctx):
    """Manage Krita projects."""
    pass
