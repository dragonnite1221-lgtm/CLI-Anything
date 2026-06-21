# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error  # noqa: E402,E501
from .sbox_cli_p5 import scene  # noqa: E402,E501
# fmt: on


@scene.command("modify-object")
@click.argument("scene_path")
@click.option("--guid", default=None, help="Object GUID to modify")
@click.option("--name-match", default=None, help="Object name to match")
@click.option("--name", "new_name", default=None, help="New name for the object")
@click.option("--position", default=None, help="New position (x,y,z)")
@click.option("--rotation", default=None, help="New rotation (x,y,z,w)")
@click.option("--scale", default=None, help="New scale (x,y,z)")
@click.option("--tags", default=None, help="New tags (comma-separated)")
@click.option("--enabled/--disabled", default=None, help="Enable or disable object")
@click.pass_context
def scene_modify_object(
    ctx,
    scene_path,
    guid,
    name_match,
    new_name,
    position,
    rotation,
    scale,
    tags,
    enabled,
):
    """Modify an existing GameObject in a scene."""
    try:
        result = scene_mod.modify_object(
            scene_path,
            guid=guid,
            name_match=name_match,
            new_name=new_name,
            position=position,
            rotation=rotation,
            scale=scale,
            tags=tags,
            enabled=enabled,
        )
        _output(
            ctx,
            result,
            lambda d: (
                f"Modified {d['name']} ({d['guid']}): {', '.join(d['modified_fields'])}"
            ),
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("set-property")
@click.argument("scene_path")
@click.option(
    "--fixed-update-freq", type=int, default=None, help="Fixed update frequency (Hz)"
)
@click.option(
    "--network-freq", type=int, default=None, help="Network update frequency (Hz)"
)
@click.option("--timescale", type=float, default=None, help="Time scale (1.0 = normal)")
@click.option("--network-interpolation/--no-network-interpolation", default=None)
@click.option("--physics-sub-steps", type=int, default=None)
@click.pass_context
def scene_set_property(
    ctx,
    scene_path,
    fixed_update_freq,
    network_freq,
    timescale,
    network_interpolation,
    physics_sub_steps,
):
    """Modify SceneProperties of a scene."""
    try:
        kwargs = {}
        if fixed_update_freq is not None:
            kwargs["fixed_update_freq"] = fixed_update_freq
        if network_freq is not None:
            kwargs["network_freq"] = network_freq
        if timescale is not None:
            kwargs["timescale"] = timescale
        if network_interpolation is not None:
            kwargs["network_interpolation"] = network_interpolation
        if physics_sub_steps is not None:
            kwargs["physics_sub_steps"] = physics_sub_steps

        if not kwargs:
            _output_error(ctx, "No properties specified to change")
            return

        result = scene_mod.set_scene_properties(scene_path, **kwargs)
        _output(ctx, result, lambda d: _format_status_block(d, "Scene Properties"))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("clone-object")
@click.argument("scene_path")
@click.option("--guid", default=None, help="GUID of object to clone")
@click.option("--name-match", default=None, help="Name of object to clone")
@click.option("--new-name", default=None, help="Name for the clone")
@click.option("--position", default=None, help="Position for the clone (x,y,z)")
@click.pass_context
def scene_clone_object(ctx, scene_path, guid, name_match, new_name, position):
    """Clone (duplicate) a GameObject with new GUIDs."""
    try:
        result = scene_mod.clone_object(
            scene_path,
            guid=guid,
            name=name_match,
            new_name=new_name,
            position=position,
        )
        _output(
            ctx,
            result,
            lambda d: f"Cloned '{d['original_name']}' -> '{d['name']}' ({d['guid']})",
        )
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))


@scene.command("get-object")
@click.argument("scene_path")
@click.option("--guid", default=None, help="Object GUID")
@click.option("--name", "name_match", default=None, help="Object name")
@click.pass_context
def scene_get_object(ctx, scene_path, guid, name_match):
    """Get full details of a single GameObject."""
    try:
        result = scene_mod.get_object(scene_path, guid=guid, name=name_match)
        _output(ctx, result, lambda d: _format_status_block(d, f"Object: {d['name']}"))
    except click.ClickException:
        raise
    except Exception as exc:
        _output_error(ctx, str(exc))
