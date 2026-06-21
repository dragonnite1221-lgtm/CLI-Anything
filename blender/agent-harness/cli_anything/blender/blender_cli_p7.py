# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p6 import camera  # noqa: E402,E501
# fmt: on


@camera.command("add")
@click.option("--name", "-n", default=None, help="Camera name")
@click.option("--location", "-l", default=None, help="Location x,y,z")
@click.option("--rotation", "-r", default=None, help="Rotation x,y,z (degrees)")
@click.option(
    "--type",
    "camera_type",
    type=click.Choice(["PERSP", "ORTHO", "PANO"]),
    default="PERSP",
)
@click.option(
    "--focal-length", "-f", type=float, default=50.0, help="Focal length (mm)"
)
@click.option("--active", is_flag=True, help="Set as active camera")
@handle_error
def camera_add(name, location, rotation, camera_type, focal_length, active):
    """Add a camera to the scene."""
    loc = [float(x) for x in location.split(",")] if location else None
    rot = [float(x) for x in rotation.split(",")] if rotation else None

    sess = get_session()
    sess.snapshot("Add camera")
    cam = light_mod.add_camera(
        sess.get_project(),
        name=name,
        location=loc,
        rotation=rot,
        camera_type=camera_type,
        focal_length=focal_length,
        set_active=active,
    )
    output(cam, f"Added camera: {cam['name']}")


@camera.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def camera_set(index, prop, value):
    """Set a camera property."""
    # Handle vector properties
    if prop in ("location", "rotation"):
        value = [float(x) for x in value.split(",")]
    sess = get_session()
    sess.snapshot(f"Set camera {index} {prop}")
    light_mod.set_camera(sess.get_project(), index, prop, value)
    output(
        {"camera": index, "property": prop, "value": value},
        f"Set camera {index} {prop}",
    )


@camera.command("set-active")
@click.argument("index", type=int)
@handle_error
def camera_set_active(index):
    """Set the active camera."""
    sess = get_session()
    sess.snapshot(f"Set active camera {index}")
    result = light_mod.set_active_camera(sess.get_project(), index)
    output(result, f"Active camera: {result['active_camera']}")


@camera.command("list")
@handle_error
def camera_list():
    """List all cameras."""
    sess = get_session()
    cameras = light_mod.list_cameras(sess.get_project())
    output(cameras, "Cameras:")


@cli.group()
def light():
    """Light management commands."""
    pass


@light.command("add")
@click.argument("light_type", type=click.Choice(["point", "sun", "spot", "area"]))
@click.option("--name", "-n", default=None, help="Light name")
@click.option("--location", "-l", default=None, help="Location x,y,z")
@click.option("--rotation", "-r", default=None, help="Rotation x,y,z (degrees)")
@click.option("--color", "-c", default=None, help="Color R,G,B (0.0-1.0)")
@click.option("--power", "-w", type=float, default=None, help="Power/energy")
@handle_error
def light_add(light_type, name, location, rotation, color, power):
    """Add a light to the scene."""
    loc = [float(x) for x in location.split(",")] if location else None
    rot = [float(x) for x in rotation.split(",")] if rotation else None
    col = [float(x) for x in color.split(",")] if color else None

    sess = get_session()
    sess.snapshot(f"Add light: {light_type}")
    lt = light_mod.add_light(
        sess.get_project(),
        light_type=light_type.upper(),
        name=name,
        location=loc,
        rotation=rot,
        color=col,
        power=power,
    )
    output(lt, f"Added {light_type} light: {lt['name']}")


@light.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def light_set(index, prop, value):
    """Set a light property."""
    # Handle vector/color properties
    if prop in ("location", "rotation", "color"):
        value = [float(x) for x in value.split(",")]
    sess = get_session()
    sess.snapshot(f"Set light {index} {prop}")
    light_mod.set_light(sess.get_project(), index, prop, value)
    output(
        {"light": index, "property": prop, "value": value}, f"Set light {index} {prop}"
    )


@light.command("list")
@handle_error
def light_list():
    """List all lights."""
    sess = get_session()
    lights = light_mod.list_lights(sess.get_project())
    output(lights, "Lights:")


@cli.group()
def animation():
    """Animation and keyframe commands."""
    pass
