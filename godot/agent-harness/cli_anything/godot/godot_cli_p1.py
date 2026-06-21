# ruff: noqa: F403, F405, E501
from .godot_cli_base import *  # noqa: F403


def _out(ctx, data: dict) -> None:
    """Print result as JSON or human-readable based on context."""
    if ctx.obj.get("json"):
        click.echo(json_mod.dumps(data, indent=2, ensure_ascii=False))
    else:
        status = data.get("status", "")
        if status == "error":
            click.secho(
                f"Error: {data.get('message', data.get('stderr', 'unknown'))}", fg="red"
            )
            return
        for key, value in data.items():
            if key == "status":
                continue
            if isinstance(value, list):
                click.secho(f"{key} ({len(value)}):", fg="cyan", bold=True)
                for item in value:
                    if isinstance(item, dict):
                        parts = [f"{k}={v}" for k, v in item.items()]
                        click.echo(f"  - {', '.join(parts)}")
                    else:
                        click.echo(f"  - {item}")
            elif isinstance(value, dict):
                click.secho(f"{key}:", fg="cyan", bold=True)
                for k, v in value.items():
                    click.echo(f"  {k}: {v}")
            else:
                click.echo(f"{key}: {value}")


def _handle_error(func):
    """Decorator to catch RuntimeError and format output."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            ctx = click.get_current_context()
            _out(ctx, {"status": "error", "message": str(e)})
            if not ctx.obj.get("repl"):
                sys.exit(1)

    return wrapper


@click.group(invoke_without_command=True)
@click.option(
    "--json", "use_json", is_flag=True, help="Output JSON for agent consumption."
)
@click.option(
    "--project", "-p", "project", default=None, help="Path to Godot project directory."
)
@click.pass_context
def cli(ctx, use_json, project):
    """cli-anything-godot — Agent-native CLI for the Godot game engine."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json
    ctx.obj["project"] = os.path.abspath(project) if project else None
    ctx.obj["repl"] = ctx.obj.get("repl", False)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.group()
@click.pass_context
def project(ctx):
    """Manage Godot projects — create, inspect, list assets."""
    pass


def _get_project(ctx) -> str:
    """Resolve project path from context or cwd."""
    p = ctx.obj.get("project") or os.getcwd()
    return os.path.abspath(p)


@project.command("create")
@click.argument("path")
@click.option("--name", default=None, help="Project display name.")
@click.pass_context
@_handle_error
def project_create(ctx, path, name):
    """Create a new Godot project at PATH."""
    from cli_anything.godot.core.project import create_project

    _out(ctx, create_project(os.path.abspath(path), name))


@project.command("info")
@click.pass_context
@_handle_error
def project_info(ctx):
    """Show project metadata from project.godot."""
    from cli_anything.godot.core.project import get_project_info

    _out(ctx, get_project_info(_get_project(ctx)))


@project.command("scenes")
@click.pass_context
@_handle_error
def project_scenes(ctx):
    """List all scene files (.tscn, .scn) in the project."""
    from cli_anything.godot.core.project import list_scenes

    _out(ctx, list_scenes(_get_project(ctx)))


@project.command("scripts")
@click.pass_context
@_handle_error
def project_scripts(ctx):
    """List all GDScript files (.gd) in the project."""
    from cli_anything.godot.core.project import list_scripts

    _out(ctx, list_scripts(_get_project(ctx)))


@project.command("resources")
@click.pass_context
@_handle_error
def project_resources(ctx):
    """List all resource files (.tres, .res) in the project."""
    from cli_anything.godot.core.project import list_resources

    _out(ctx, list_resources(_get_project(ctx)))


@project.command("reimport")
@click.pass_context
@_handle_error
def project_reimport(ctx):
    """Force re-import of all project resources via Godot."""
    from cli_anything.godot.core.project import reimport_project

    _out(ctx, reimport_project(_get_project(ctx)))


@cli.group()
@click.pass_context
def scene(ctx):
    """Create and inspect Godot scenes."""
    pass


@scene.command("create")
@click.argument("scene_path")
@click.option(
    "--root-type", default="Node2D", help="Root node type (Node2D, Node3D, Control...)."
)
@click.option("--root-name", default=None, help="Root node name.")
@click.pass_context
@_handle_error
def scene_create(ctx, scene_path, root_type, root_name):
    """Create a new .tscn scene file at SCENE_PATH (relative to project)."""
    from cli_anything.godot.core.scene import create_scene

    _out(ctx, create_scene(_get_project(ctx), scene_path, root_type, root_name))


@scene.command("read")
@click.argument("scene_path")
@click.pass_context
@_handle_error
def scene_read(ctx, scene_path):
    """Parse and display the node tree of a .tscn scene."""
    from cli_anything.godot.core.scene import read_scene

    _out(ctx, read_scene(_get_project(ctx), scene_path))
