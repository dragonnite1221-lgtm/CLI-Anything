# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_points, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p4 import part_group  # noqa: E402,E501
# fmt: on


@part_group.command("slice")
@click.argument("index", type=int)
@click.option(
    "--plane", default="XY", type=click.Choice(["XY", "XZ", "YZ"]), help="Slice plane."
)
@click.option("--offset", default=0.0, type=float, help="Plane offset.")
@handle_error
def part_slice(index: int, plane: str, offset: float) -> None:
    """Slice a part into two halves."""
    sess = get_session()
    sess.snapshot(f"Slice part #{index}")
    proj = sess.get_project()
    result = parts_mod.slice_part(proj, index, plane=plane, offset=offset)
    output_fn(result, "Sliced part into two halves")


@part_group.command("line-3d")
@click.option("--start", "-s", default="0,0,0", help="Start point x,y,z.")
@click.option("--end", "-e", default="10,0,0", help="End point x,y,z.")
@click.option("--name", "-n", help="Part name.")
@handle_error
def part_line_3d(start: str, end: str, name: Optional[str]) -> None:
    """Add a 3D line (edge) between two points."""
    sess = get_session()
    sess.snapshot("Add line-3d")
    proj = sess.get_project()
    s = _parse_vec3(start)
    e = _parse_vec3(end)
    result = parts_mod.add_line_3d(proj, start=s, end=e, name=name)
    output_fn(result, f"Added line-3d: {result.get('name', '')}")


@part_group.command("wire")
@click.argument("points_str", type=str)
@click.option("--closed", is_flag=True, help="Close the wire.")
@click.option("--name", "-n", help="Part name.")
@handle_error
def part_wire(points_str: str, closed: bool, name: Optional[str]) -> None:
    """Add a wire from semicolon-separated x,y,z points."""
    sess = get_session()
    sess.snapshot("Add wire")
    proj = sess.get_project()
    pts = _parse_points(points_str)
    result = parts_mod.add_wire(proj, points=pts, closed=closed, name=name)
    output_fn(result, f"Added wire: {result.get('name', '')}")


@part_group.command("polygon-3d")
@click.option("--center", "-c", default="0,0,0", help="Center x,y,z.")
@click.option("--sides", default=6, type=int, help="Number of sides.")
@click.option("--radius", "-r", default=5.0, type=float, help="Radius.")
@click.option("--normal", default="0,0,1", help="Normal vector x,y,z.")
@click.option("--name", "-n", help="Part name.")
@handle_error
def part_polygon_3d(
    center: str, sides: int, radius: float, normal: str, name: Optional[str]
) -> None:
    """Add a regular polygon in 3D space."""
    sess = get_session()
    sess.snapshot("Add polygon-3d")
    proj = sess.get_project()
    c = _parse_vec3(center)
    n = _parse_vec3(normal)
    result = parts_mod.add_polygon_3d(
        proj, center=c, sides=sides, radius=radius, normal=n, name=name
    )
    output_fn(result, f"Added polygon-3d: {result.get('name', '')}")


@part_group.command("info")
@click.argument("index", type=int)
@handle_error
def part_info(index: int) -> None:
    """Get detailed information about a part."""
    sess = get_session()
    proj = sess.get_project()
    result = parts_mod.part_info(proj, index)
    output_fn(result, f"Part #{index} info:")


@part_group.command("bounds")
@click.argument("index", type=int)
@handle_error
def part_bounds(index: int) -> None:
    """Get local and world bounding boxes for a part."""
    sess = get_session()
    proj = sess.get_project()
    result = parts_mod.part_bounds(proj, index)
    output_fn(result, f"Part #{index} bounds:")
