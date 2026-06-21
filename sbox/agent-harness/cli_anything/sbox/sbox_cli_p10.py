# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p5 import scene  # noqa: E402,E501
# fmt: on


@scene.command("instantiate-prefab")
@click.argument("scene_path")
@click.argument("prefab_path")
@click.option(
    "--name",
    default=None,
    help="Override the GameObject name (defaults to prefab root name)",
)
@click.option("--position", default="0,0,0", help="Position 'x,y,z'")
@click.option("--rotation", default="0,0,0,1", help="Rotation 'x,y,z,w'")
@click.option("--scale", default="1,1,1", help="Scale 'x,y,z'")
@click.option("--parent-guid", default=None, help="Optional parent GameObject GUID")
@click.pass_context
def scene_instantiate_prefab(
    ctx, scene_path, prefab_path, name, position, rotation, scale, parent_guid
):
    """Insert a prefab reference into a scene as a new GameObject (PrefabSource)."""
    try:
        new_guid = scene_mod.instantiate_prefab(
            scene_path,
            prefab_path,
            name=name,
            position=position,
            rotation=rotation,
            scale=scale,
            parent_guid=parent_guid,
        )
        result = {"guid": new_guid, "scene": scene_path, "prefab": prefab_path}
        _output(ctx, result, lambda d: f"Instantiated prefab as GameObject {d['guid']}")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@cli.group()
@click.pass_context
def prefab(ctx):
    """Manage s&box prefabs."""
    pass


@prefab.command("new")
@click.option("--name", required=True, help="Prefab name")
@click.option("-o", "--output", "output_path", default=None, help="Output file path")
@click.option("--components", default=None, help="Comma-separated preset names")
@click.pass_context
def prefab_new(ctx, name, output_path, components):
    """Create a new prefab."""
    try:
        if not output_path:
            output_path = f"{name}.prefab"

        comp_list = None
        if components:
            comp_list = [c.strip() for c in components.split(",")]

        result = prefab_mod.create_prefab(
            name=name,
            output_path=output_path,
            components=comp_list,
        )
        info = {
            "name": name,
            "path": os.path.abspath(output_path),
            "root_guid": result.get("RootObject", {}).get("__guid", ""),
        }
        _output(
            ctx,
            info,
            lambda d: _format_status_block(d, f"Prefab '{d['name']}' created"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("info")
@click.argument("prefab_path")
@click.pass_context
def prefab_info(ctx, prefab_path):
    """Show prefab info."""
    try:
        result = prefab_mod.get_prefab_info(prefab_path)
        _output(
            ctx,
            result,
            lambda d: _format_status_block(d, f"Prefab: {d.get('name', '')}"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@prefab.command("from-scene")
@click.argument("scene_path")
@click.argument("object_guid")
@click.option(
    "-o", "--output", "output_path", default=None, help="Output prefab file path"
)
@click.pass_context
def prefab_from_scene(ctx, scene_path, object_guid, output_path):
    """Extract a GameObject from a scene as a prefab."""
    try:
        if not output_path:
            output_path = f"{object_guid}.prefab"
        result = prefab_mod.from_scene_object(
            scene_path=scene_path,
            object_guid=object_guid,
            output_path=output_path,
        )
        info = {
            "name": result.get("RootObject", {}).get("Name", ""),
            "path": os.path.abspath(output_path),
            "guid": result.get("RootObject", {}).get("__guid", ""),
        }
        _output(
            ctx,
            info,
            lambda d: _format_status_block(d, f"Prefab extracted: {d.get('name', '')}"),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))
