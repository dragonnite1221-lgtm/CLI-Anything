# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p3 import scene  # noqa: E402,E501
# fmt: on


@scene.command("new")
@click.option("--name", "-n", default="untitled", help="Scene name")
@click.option("--profile", "-p", type=str, default=None, help="Scene profile")
@click.option(
    "--resolution-x", "-rx", type=int, default=1920, help="Horizontal resolution"
)
@click.option(
    "--resolution-y", "-ry", type=int, default=1080, help="Vertical resolution"
)
@click.option(
    "--engine", type=click.Choice(["CYCLES", "EEVEE", "WORKBENCH"]), default="CYCLES"
)
@click.option("--samples", type=int, default=128, help="Render samples")
@click.option("--fps", type=int, default=24, help="Frames per second")
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def scene_new(name, profile, resolution_x, resolution_y, engine, samples, fps, output):
    """Create a new scene."""
    proj = scene_mod.create_scene(
        name=name,
        profile=profile,
        resolution_x=resolution_x,
        resolution_y=resolution_y,
        engine=engine,
        samples=samples,
        fps=fps,
    )
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        scene_mod.save_scene(proj, output)
    output_data = scene_mod.get_scene_info(proj)
    globals()["output"](output_data, f"Created scene: {name}")


@scene.command("open")
@click.argument("path")
@handle_error
def scene_open(path):
    """Open an existing scene."""
    proj = scene_mod.open_scene(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = scene_mod.get_scene_info(proj)
    output(info, f"Opened: {path}")


@scene.command("save")
@click.argument("path", required=False)
@handle_error
def scene_save(path):
    """Save the current scene."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@scene.command("info")
@handle_error
def scene_info():
    """Show scene information."""
    sess = get_session()
    info = scene_mod.get_scene_info(sess.get_project())
    output(info)


@scene.command("profiles")
@handle_error
def scene_profiles():
    """List available scene profiles."""
    profiles = scene_mod.list_profiles()
    output(profiles, "Available profiles:")


@scene.command("json")
@handle_error
def scene_json():
    """Print raw scene JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group("object")
def object_group():
    """3D object management commands."""
    pass


@object_group.command("add")
@click.argument(
    "mesh_type",
    type=click.Choice(
        ["cube", "sphere", "cylinder", "cone", "plane", "torus", "monkey", "empty"]
    ),
)
@click.option("--name", "-n", default=None, help="Object name")
@click.option("--location", "-l", default=None, help="Location x,y,z")
@click.option("--rotation", "-r", default=None, help="Rotation x,y,z (degrees)")
@click.option("--scale", "-s", default=None, help="Scale x,y,z")
@click.option("--param", "-p", multiple=True, help="Mesh parameter: key=value")
@click.option("--collection", "-c", default=None, help="Target collection")
@handle_error
def object_add(mesh_type, name, location, rotation, scale, param, collection):
    """Add a 3D primitive object."""
    loc = [float(x) for x in location.split(",")] if location else None
    rot = [float(x) for x in rotation.split(",")] if rotation else None
    scl = [float(x) for x in scale.split(",")] if scale else None

    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Invalid param format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        params[k] = v

    sess = get_session()
    sess.snapshot(f"Add object: {mesh_type}")
    proj = sess.get_project()
    obj = obj_mod.add_object(
        proj,
        mesh_type=mesh_type,
        name=name,
        location=loc,
        rotation=rot,
        scale=scl,
        mesh_params=params if params else None,
        collection=collection,
    )
    output(obj, f"Added {mesh_type}: {obj['name']}")


@object_group.command("remove")
@click.argument("index", type=int)
@handle_error
def object_remove(index):
    """Remove an object by index."""
    sess = get_session()
    sess.snapshot(f"Remove object {index}")
    removed = obj_mod.remove_object(sess.get_project(), index)
    output(removed, f"Removed object {index}: {removed.get('name', '')}")
