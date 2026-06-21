# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec2, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p4 import part_group  # noqa: E402,E501
# fmt: on


@part_group.command("align")
@click.argument("index", type=int)
@click.argument("target_index", type=int)
@click.option(
    "--x", "x_anchor", type=str, help="Source anchor on x axis (min|center|max)."
)
@click.option(
    "--to-x", "to_x_anchor", type=str, help="Target anchor on x axis (min|center|max)."
)
@click.option(
    "--dx", default=0.0, type=float, help="Additional x offset after alignment."
)
@click.option(
    "--y", "y_anchor", type=str, help="Source anchor on y axis (min|center|max)."
)
@click.option(
    "--to-y", "to_y_anchor", type=str, help="Target anchor on y axis (min|center|max)."
)
@click.option(
    "--dy", default=0.0, type=float, help="Additional y offset after alignment."
)
@click.option(
    "--z", "z_anchor", type=str, help="Source anchor on z axis (min|center|max)."
)
@click.option(
    "--to-z", "to_z_anchor", type=str, help="Target anchor on z axis (min|center|max)."
)
@click.option(
    "--dz", default=0.0, type=float, help="Additional z offset after alignment."
)
@handle_error
def part_align(
    index: int,
    target_index: int,
    x_anchor: Optional[str],
    to_x_anchor: Optional[str],
    dx: float,
    y_anchor: Optional[str],
    to_y_anchor: Optional[str],
    dy: float,
    z_anchor: Optional[str],
    to_z_anchor: Optional[str],
    dz: float,
) -> None:
    """Align a part to another part using world bounding-box anchors."""
    sess = get_session()
    sess.snapshot(f"Align part #{index} to #{target_index}")
    proj = sess.get_project()
    result = parts_mod.align_part(
        proj,
        index,
        target_index,
        x=x_anchor,
        to_x=to_x_anchor,
        dx=dx,
        y=y_anchor,
        to_y=to_y_anchor,
        dy=dy,
        z=z_anchor,
        to_z=to_z_anchor,
        dz=dz,
    )
    output_fn(result, f"Aligned part #{index} to #{target_index}")


@cli.group("sketch")
def sketch_group():
    """2D sketch commands."""
    pass


@sketch_group.command("new")
@click.option("--name", "-n", help="Sketch name.")
@click.option(
    "--plane", default="XY", type=click.Choice(["XY", "XZ", "YZ"]), help="Sketch plane."
)
@click.option("--offset", default=0.0, type=float, help="Plane offset.")
@handle_error
def sketch_new(name: Optional[str], plane: str, offset: float) -> None:
    """Create a new sketch."""
    sess = get_session()
    sess.snapshot("New sketch")
    proj = sess.get_project()
    result = sketch_mod.create_sketch(proj, name=name, plane=plane, offset=offset)
    output_fn(result, f"Created sketch: {result.get('name', '')}")


@sketch_group.command("add-line")
@click.argument("sketch_index", type=int)
@click.option("--start", "-s", default="0,0", help="Start point x,y.")
@click.option("--end", "-e", default="10,0", help="End point x,y.")
@handle_error
def sketch_add_line(sketch_index: int, start: str, end: str) -> None:
    """Add a line to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add line to sketch #{sketch_index}")
    proj = sess.get_project()
    s = _parse_vec2(start)
    e = _parse_vec2(end)
    result = sketch_mod.add_line(proj, sketch_index, start=s, end=e)
    output_fn(result, "Added line")


@sketch_group.command("add-circle")
@click.argument("sketch_index", type=int)
@click.option("--center", "-c", default="0,0", help="Center x,y.")
@click.option("--radius", "-r", default=5.0, type=float, help="Radius.")
@handle_error
def sketch_add_circle(sketch_index: int, center: str, radius: float) -> None:
    """Add a circle to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add circle to sketch #{sketch_index}")
    proj = sess.get_project()
    c = _parse_vec2(center)
    result = sketch_mod.add_circle(proj, sketch_index, center=c, radius=radius)
    output_fn(result, "Added circle")


@sketch_group.command("add-rect")
@click.argument("sketch_index", type=int)
@click.option("--corner", "-c", default="0,0", help="Corner x,y.")
@click.option("--width", "-w", default=10.0, type=float, help="Width.")
@click.option("--height", "-h", default=10.0, type=float, help="Height.")
@handle_error
def sketch_add_rect(
    sketch_index: int, corner: str, width: float, height: float
) -> None:
    """Add a rectangle to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add rectangle to sketch #{sketch_index}")
    proj = sess.get_project()
    c = _parse_vec2(corner)
    result = sketch_mod.add_rectangle(
        proj, sketch_index, corner=c, width=width, height=height
    )
    output_fn(result, "Added rectangle")
