# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _output, _output_error  # noqa: E402,E501
from .sbox_cli_p5 import scene  # noqa: E402,E501
# fmt: on


@scene.command("add-object")
@click.argument("scene_path")
@click.argument("name")
@click.option("--position", default="0,0,0", help="Position as x,y,z")
@click.option("--rotation", default="0,0,0,1", help="Rotation as x,y,z,w quaternion")
@click.option("--scale", default="1,1,1", help="Scale as x,y,z")
@click.option("--tags", default="", help="Space-separated tags")
@click.option(
    "--components",
    default=None,
    help="Comma-separated preset names (e.g. model,box_collider,rigidbody)",
)
@click.option("--parent", default=None, help="Parent object GUID")
@click.pass_context
def scene_add_object(
    ctx, scene_path, name, position, rotation, scale, tags, components, parent
):
    """Add a GameObject to a scene."""
    try:
        comp_list = None
        if components:
            comp_list = [c.strip() for c in components.split(",")]

        new_guid = scene_mod.add_object(
            scene_path=scene_path,
            name=name,
            position=position,
            rotation=rotation,
            scale=scale,
            tags=tags,
            components=comp_list,
            parent_guid=parent,
        )
        result = {"guid": new_guid, "name": name, "scene": scene_path}
        _output(
            ctx, result, lambda d: f"Added '{d['name']}' ({d['guid']}) to {d['scene']}"
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("remove-object")
@click.argument("scene_path")
@click.option("--name", default=None, help="Object name to remove")
@click.option("--guid", default=None, help="Object GUID to remove")
@click.pass_context
def scene_remove_object(ctx, scene_path, name, guid):
    """Remove a GameObject from a scene."""
    try:
        if not name and not guid:
            raise click.ClickException("Must specify --name or --guid")
        removed = scene_mod.remove_object(scene_path, name=name, guid=guid)
        result = {"removed": removed, "name": name, "guid": guid}
        if removed:
            _output(ctx, result, lambda d: f"Removed object from {scene_path}")
        else:
            _output(ctx, result, lambda d: f"Object not found in {scene_path}")
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("add-component")
@click.argument("scene_path")
@click.argument("object_guid")
@click.argument("component_type")
@click.option("--properties", default=None, help="Component properties as JSON string")
@click.pass_context
def scene_add_component(ctx, scene_path, object_guid, component_type, properties):
    """Add a component to a GameObject."""
    try:
        props = None
        if properties:
            props = json.loads(properties)
        comp_guid = scene_mod.add_component(
            scene_path=scene_path,
            object_guid=object_guid,
            component_type=component_type,
            properties=props,
        )
        result = {
            "component_guid": comp_guid,
            "type": component_type,
            "object_guid": object_guid,
        }
        _output(
            ctx,
            result,
            lambda d: (
                f"Added {d['type']} ({d['component_guid']}) to object {d['object_guid']}"
            ),
        )
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("remove-component")
@click.argument("scene_path")
@click.argument("object_guid")
@click.option("--component-guid", default=None, help="Component GUID to remove")
@click.option(
    "--component-type",
    default=None,
    help="Component type to remove (e.g. Sandbox.Rigidbody)",
)
@click.pass_context
def scene_remove_component(
    ctx, scene_path, object_guid, component_guid, component_type
):
    """Remove a component from a GameObject."""
    try:
        if not component_guid and not component_type:
            _output_error(ctx, "Must provide --component-guid or --component-type")
            return
        removed = scene_mod.remove_component(
            scene_path,
            object_guid,
            component_guid=component_guid,
            component_type=component_type,
        )
        result = {"removed": removed, "object_guid": object_guid}
        _output(
            ctx,
            result,
            lambda d: f"Component {'removed' if d['removed'] else 'not found'}",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
