# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p7 import animation  # noqa: E402,E501
# fmt: on


@animation.command("keyframe")
@click.argument("object_index", type=int)
@click.argument("frame", type=int)
@click.argument("prop")
@click.argument("value")
@click.option(
    "--interpolation",
    "-i",
    type=click.Choice(["CONSTANT", "LINEAR", "BEZIER"]),
    default="BEZIER",
)
@handle_error
def animation_keyframe(object_index, frame, prop, value, interpolation):
    """Set a keyframe on an object."""
    # Handle vector values
    if prop in ("location", "rotation", "scale"):
        value = [float(x) for x in value.split(",")]
    sess = get_session()
    sess.snapshot(f"Add keyframe at frame {frame}")
    result = anim_mod.add_keyframe(
        sess.get_project(),
        object_index,
        frame,
        prop,
        value,
        interpolation,
    )
    output(result, f"Keyframe set at frame {frame}")


@animation.command("remove-keyframe")
@click.argument("object_index", type=int)
@click.argument("frame", type=int)
@click.option(
    "--prop", "-p", default=None, help="Property (remove all at frame if not specified)"
)
@handle_error
def animation_remove_keyframe(object_index, frame, prop):
    """Remove a keyframe from an object."""
    sess = get_session()
    sess.snapshot(f"Remove keyframe at frame {frame}")
    removed = anim_mod.remove_keyframe(sess.get_project(), object_index, frame, prop)
    output(removed, f"Removed {len(removed)} keyframe(s) at frame {frame}")


@animation.command("frame-range")
@click.argument("start", type=int)
@click.argument("end", type=int)
@handle_error
def animation_frame_range(start, end):
    """Set the animation frame range."""
    sess = get_session()
    sess.snapshot("Set frame range")
    result = anim_mod.set_frame_range(sess.get_project(), start, end)
    output(result, f"Frame range: {start}-{end}")


@animation.command("fps")
@click.argument("fps", type=int)
@handle_error
def animation_fps(fps):
    """Set the animation FPS."""
    sess = get_session()
    result = anim_mod.set_fps(sess.get_project(), fps)
    output(result, f"FPS set to {fps}")


@animation.command("list-keyframes")
@click.argument("object_index", type=int)
@click.option("--prop", "-p", default=None, help="Filter by property")
@handle_error
def animation_list_keyframes(object_index, prop):
    """List keyframes for an object."""
    sess = get_session()
    keyframes = anim_mod.list_keyframes(sess.get_project(), object_index, prop)
    output(keyframes, f"Keyframes for object {object_index}:")


@cli.group("render")
def render_group():
    """Render settings and output commands."""
    pass


@render_group.command("settings")
@click.option(
    "--engine", type=click.Choice(["CYCLES", "EEVEE", "WORKBENCH"]), default=None
)
@click.option("--resolution-x", "-rx", type=int, default=None)
@click.option("--resolution-y", "-ry", type=int, default=None)
@click.option("--resolution-percentage", type=int, default=None)
@click.option("--samples", type=int, default=None)
@click.option("--denoising/--no-denoising", default=None)
@click.option("--transparent/--no-transparent", default=None)
@click.option("--format", "output_format", default=None)
@click.option("--output-path", default=None)
@click.option("--preset", default=None, help="Apply render preset")
@handle_error
def render_settings(
    engine,
    resolution_x,
    resolution_y,
    resolution_percentage,
    samples,
    denoising,
    transparent,
    output_format,
    output_path,
    preset,
):
    """Configure render settings."""
    sess = get_session()
    sess.snapshot("Update render settings")
    result = render_mod.set_render_settings(
        sess.get_project(),
        engine=engine,
        resolution_x=resolution_x,
        resolution_y=resolution_y,
        resolution_percentage=resolution_percentage,
        samples=samples,
        use_denoising=denoising,
        film_transparent=transparent,
        output_format=output_format,
        output_path=output_path,
        preset=preset,
    )
    output(result, "Render settings updated")


@render_group.command("info")
@handle_error
def render_info():
    """Show current render settings."""
    sess = get_session()
    info = render_mod.get_render_settings(sess.get_project())
    output(info)


@render_group.command("presets")
@handle_error
def render_presets():
    """List available render presets."""
    presets = render_mod.list_render_presets()
    output(presets, "Render presets:")
