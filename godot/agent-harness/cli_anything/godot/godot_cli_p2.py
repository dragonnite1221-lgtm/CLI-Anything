# ruff: noqa: F403, F405, E501
from .godot_cli_base import *  # noqa: F403

# fmt: off
from .godot_cli_p1 import _get_project, _handle_error, _out, cli, scene  # noqa: E402,E501
# fmt: on


@scene.command("add-node")
@click.argument("scene_path")
@click.option("--name", "node_name", required=True, help="Name of the new node.")
@click.option(
    "--type", "node_type", required=True, help="Node type (Sprite2D, Camera2D, etc.)."
)
@click.option("--parent", default=".", help="Parent node path (default: root).")
@click.pass_context
@_handle_error
def scene_add_node(ctx, scene_path, node_name, node_type, parent):
    """Add a child node to an existing scene."""
    from cli_anything.godot.core.scene import add_node

    _out(ctx, add_node(_get_project(ctx), scene_path, node_name, node_type, parent))


@cli.group("export")
@click.pass_context
def export_group(ctx):
    """Export Godot projects to target platforms."""
    pass


@export_group.command("build")
@click.option(
    "--preset",
    default=None,
    help="Export preset name. Omit to export all (Godot 4.3+).",
)
@click.option("--output", default=None, help="Output file path.")
@click.option("--debug", is_flag=True, help="Use debug export instead of release.")
@click.pass_context
@_handle_error
def export_build(ctx, preset, output, debug):
    """Build/export the project using configured presets."""
    from cli_anything.godot.core.export import export_project

    _out(ctx, export_project(_get_project(ctx), preset, output, debug))


@export_group.command("presets")
@click.pass_context
@_handle_error
def export_presets(ctx):
    """List configured export presets."""
    from cli_anything.godot.core.export import list_export_presets

    _out(ctx, list_export_presets(_get_project(ctx)))


@cli.group()
@click.pass_context
def script(ctx):
    """Run and validate GDScript files."""
    pass


@script.command("run")
@click.argument("script_path")
@click.option("--timeout", default=60, help="Execution timeout in seconds.")
@click.pass_context
@_handle_error
def script_run(ctx, script_path, timeout):
    """Execute a GDScript file in headless mode. Must extend SceneTree."""
    from cli_anything.godot.core.script import run_script

    _out(ctx, run_script(_get_project(ctx), script_path, timeout))


@script.command("inline")
@click.argument("code")
@click.option("--timeout", default=60, help="Execution timeout in seconds.")
@click.pass_context
@_handle_error
def script_inline(ctx, code, timeout):
    """Run inline GDScript code (wrapped in SceneTree._init).

    Security: The provided code is written to a temp file and executed via
    Godot subprocess. Only use with trusted input.
    """
    from cli_anything.godot.core.script import run_inline

    _out(ctx, run_inline(_get_project(ctx), code, timeout))


@script.command("validate")
@click.argument("script_path")
@click.pass_context
@_handle_error
def script_validate(ctx, script_path):
    """Validate GDScript syntax without executing."""
    from cli_anything.godot.core.script import validate_script

    _out(ctx, validate_script(_get_project(ctx), script_path))


@cli.group()
@click.pass_context
def engine(ctx):
    """Godot engine info — version, status."""
    pass


@engine.command("version")
@click.pass_context
@_handle_error
def engine_version(ctx):
    """Show Godot engine version."""
    _out(ctx, get_version())


@engine.command("status")
@click.pass_context
@_handle_error
def engine_status(ctx):
    """Check if Godot binary is available."""
    available = is_available()
    binary = find_godot_binary()
    _out(
        ctx,
        {
            "status": "ok",
            "available": available,
            "binary": binary or "not found",
        },
    )
