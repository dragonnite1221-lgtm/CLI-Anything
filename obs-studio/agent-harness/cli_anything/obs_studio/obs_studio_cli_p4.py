# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .obs_studio_cli_p3 import source_group  # noqa: E402,E501
# fmt: on


@source_group.command("add")
@click.argument("source_type", type=click.Choice(sorted(src_mod.SOURCE_TYPES.keys())))
@click.option("--name", "-n", default=None, help="Source name")
@click.option("--scene", "-s", "scene_index", type=int, default=0, help="Scene index")
@click.option("--position", "-p", default=None, help="Position x,y")
@click.option("--size", default=None, help="Size widthxheight")
@click.option("--setting", "-S", multiple=True, help="Setting: key=value")
@handle_error
def source_add(source_type, name, scene_index, position, size, setting):
    """Add a source to a scene."""
    pos = None
    if position:
        parts = position.split(",")
        pos = {"x": float(parts[0]), "y": float(parts[1])}
    sz = None
    if size:
        parts = size.split("x")
        sz = {"width": int(parts[0]), "height": int(parts[1])}
    settings = {}
    for s in setting:
        if "=" not in s:
            raise ValueError(f"Invalid setting format: '{s}'. Use key=value.")
        k, v = s.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        settings[k] = v

    sess = get_session()
    sess.snapshot(f"Add source: {source_type}")
    src = src_mod.add_source(
        sess.get_project(),
        source_type,
        scene_index=scene_index,
        name=name,
        position=pos,
        size=sz,
        settings=settings if settings else None,
    )
    output(src, f"Added {source_type}: {src['name']}")


@source_group.command("remove")
@click.argument("index", type=int)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def source_remove(index, scene_index):
    """Remove a source by index."""
    sess = get_session()
    sess.snapshot(f"Remove source {index}")
    removed = src_mod.remove_source(sess.get_project(), index, scene_index)
    output(removed, f"Removed source: {removed['name']}")


@source_group.command("duplicate")
@click.argument("index", type=int)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def source_duplicate(index, scene_index):
    """Duplicate a source."""
    sess = get_session()
    sess.snapshot(f"Duplicate source {index}")
    dup = src_mod.duplicate_source(sess.get_project(), index, scene_index)
    output(dup, f"Duplicated source: {dup['name']}")


@source_group.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def source_set(index, prop, value, scene_index):
    """Set a source property (name, visible, locked, opacity, rotation)."""
    sess = get_session()
    sess.snapshot(f"Set source {index} {prop}={value}")
    src = src_mod.set_source_property(
        sess.get_project(), index, prop, value, scene_index
    )
    output(
        {"source": index, "property": prop, "value": value},
        f"Set source {index} {prop} = {value}",
    )


@source_group.command("transform")
@click.argument("index", type=int)
@click.option("--position", "-p", default=None, help="Position x,y")
@click.option("--size", default=None, help="Size widthxheight")
@click.option("--crop", default=None, help="Crop top,bottom,left,right")
@click.option("--rotation", "-r", type=float, default=None)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def source_transform(index, position, size, crop, rotation, scene_index):
    """Transform a source (position, size, crop, rotation)."""
    pos = None
    if position:
        parts = position.split(",")
        pos = {"x": float(parts[0]), "y": float(parts[1])}
    sz = None
    if size:
        parts = size.split("x")
        sz = {"width": int(parts[0]), "height": int(parts[1])}
    cr = None
    if crop:
        parts = crop.split(",")
        cr = {
            "top": int(parts[0]),
            "bottom": int(parts[1]),
            "left": int(parts[2]),
            "right": int(parts[3]),
        }

    sess = get_session()
    sess.snapshot(f"Transform source {index}")
    src = src_mod.transform_source(
        sess.get_project(),
        index,
        scene_index,
        position=pos,
        size=sz,
        crop=cr,
        rotation=rotation,
    )
    output(src, f"Transformed source {index}: {src['name']}")


@source_group.command("list")
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def source_list(scene_index):
    """List all sources in a scene."""
    sess = get_session()
    sources = src_mod.list_sources(sess.get_project(), scene_index)
    output(sources, "Sources:")
