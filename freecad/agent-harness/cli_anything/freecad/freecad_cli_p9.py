# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec2, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p8 import sketch_group  # noqa: E402,E501
# fmt: on


@sketch_group.command("add-arc")
@click.argument("sketch_index", type=int)
@click.option("--center", "-c", default="0,0", help="Center x,y.")
@click.option("--radius", "-r", default=5.0, type=float, help="Radius.")
@click.option("--start-angle", default=0.0, type=float, help="Start angle (deg).")
@click.option("--end-angle", default=90.0, type=float, help="End angle (deg).")
@handle_error
def sketch_add_arc(
    sketch_index: int, center: str, radius: float, start_angle: float, end_angle: float
) -> None:
    """Add an arc to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add arc to sketch #{sketch_index}")
    proj = sess.get_project()
    c = _parse_vec2(center)
    result = sketch_mod.add_arc(
        proj,
        sketch_index,
        center=c,
        radius=radius,
        start_angle=start_angle,
        end_angle=end_angle,
    )
    output_fn(result, "Added arc")


@sketch_group.command("constrain")
@click.argument("sketch_index", type=int)
@click.argument("constraint_type")
@click.option("--elements", "-e", required=True, help="Element indices (comma-sep).")
@click.option("--value", "-v", type=float, help="Constraint value.")
@handle_error
def sketch_constrain(
    sketch_index: int, constraint_type: str, elements: str, value: Optional[float]
) -> None:
    """Add a constraint to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add constraint to sketch #{sketch_index}")
    proj = sess.get_project()
    elems = [int(x.strip()) for x in elements.split(",")]
    result = sketch_mod.add_constraint(
        proj, sketch_index, constraint_type, elems, value=value
    )
    output_fn(result, f"Added constraint: {constraint_type}")


@sketch_group.command("close")
@click.argument("sketch_index", type=int)
@handle_error
def sketch_close(sketch_index: int) -> None:
    """Close/finalize a sketch."""
    sess = get_session()
    sess.snapshot(f"Close sketch #{sketch_index}")
    proj = sess.get_project()
    result = sketch_mod.close_sketch(proj, sketch_index)
    output_fn(result, "Sketch closed")


@sketch_group.command("list")
@handle_error
def sketch_list() -> None:
    """List all sketches."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.list_sketches(proj)
    output_fn(result, f"{len(result)} sketch(es):")


@sketch_group.command("get")
@click.argument("index", type=int)
@handle_error
def sketch_get(index: int) -> None:
    """Get sketch details."""
    sess = get_session()
    proj = sess.get_project()
    result = sketch_mod.get_sketch(proj, index)
    output_fn(result, f"Sketch #{index}:")


@sketch_group.command("add-point")
@click.argument("sketch_index", type=int)
@click.option("--position", "-p", default="0,0", help="Position x,y.")
@handle_error
def sketch_add_point(sketch_index: int, position: str) -> None:
    """Add a point to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add point to sketch #{sketch_index}")
    proj = sess.get_project()
    pos = _parse_vec2(position)
    result = sketch_mod.add_point(proj, sketch_index, position=pos)
    output_fn(result, "Added point")


@sketch_group.command("add-ellipse")
@click.argument("sketch_index", type=int)
@click.option("--center", "-c", default="0,0", help="Center x,y.")
@click.option("--major-radius", default=10.0, type=float, help="Semi-major axis.")
@click.option("--minor-radius", default=5.0, type=float, help="Semi-minor axis.")
@click.option("--angle", default=0.0, type=float, help="Rotation angle (deg).")
@handle_error
def sketch_add_ellipse(
    sketch_index: int,
    center: str,
    major_radius: float,
    minor_radius: float,
    angle: float,
) -> None:
    """Add an ellipse to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add ellipse to sketch #{sketch_index}")
    proj = sess.get_project()
    c = _parse_vec2(center)
    result = sketch_mod.add_ellipse(
        proj,
        sketch_index,
        center=c,
        major_radius=major_radius,
        minor_radius=minor_radius,
        angle=angle,
    )
    output_fn(result, "Added ellipse")


@sketch_group.command("add-polygon")
@click.argument("sketch_index", type=int)
@click.option("--center", "-c", default="0,0", help="Center x,y.")
@click.option("--sides", default=6, type=int, help="Number of sides.")
@click.option("--radius", "-r", default=5.0, type=float, help="Radius.")
@handle_error
def sketch_add_polygon(
    sketch_index: int, center: str, sides: int, radius: float
) -> None:
    """Add a regular polygon to a sketch."""
    sess = get_session()
    sess.snapshot(f"Add polygon to sketch #{sketch_index}")
    proj = sess.get_project()
    c = _parse_vec2(center)
    result = sketch_mod.add_polygon_sketch(
        proj, sketch_index, center=c, sides=sides, radius=radius
    )
    output_fn(result, "Added polygon")
