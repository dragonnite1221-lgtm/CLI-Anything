# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_points, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p27 import draft_group  # noqa: E402,E501
# fmt: on


@draft_group.command("rectangle")
@click.option("--length", "-l", default=10.0, type=float)
@click.option("--height", "-h", default=10.0, type=float)
@click.option("--name", "-n", help="Object name.")
@click.option("--position", "-pos", help="Position x,y,z.")
@handle_error
def draft_rectangle(
    length: float, height: float, name: Optional[str], position: Optional[str]
) -> None:
    """Create a 2D rectangle."""
    sess = get_session()
    sess.snapshot("Draft rectangle")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    result = draft_mod.draft_rectangle(
        proj, length=length, height=height, name=name, position=pos
    )
    output_fn(result, f"Created rectangle: {result.get('name', '')}")


@draft_group.command("circle")
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--name", "-n", help="Object name.")
@click.option("--position", "-pos", help="Position x,y,z.")
@handle_error
def draft_circle(radius: float, name: Optional[str], position: Optional[str]) -> None:
    """Create a 2D circle."""
    sess = get_session()
    sess.snapshot("Draft circle")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    result = draft_mod.draft_circle(proj, radius=radius, name=name, position=pos)
    output_fn(result, f"Created circle: {result.get('name', '')}")


@draft_group.command("ellipse")
@click.option("--major-radius", default=10.0, type=float)
@click.option("--minor-radius", default=5.0, type=float)
@click.option("--name", "-n", help="Object name.")
@click.option("--position", "-pos", help="Position x,y,z.")
@handle_error
def draft_ellipse(
    major_radius: float,
    minor_radius: float,
    name: Optional[str],
    position: Optional[str],
) -> None:
    """Create a 2D ellipse."""
    sess = get_session()
    sess.snapshot("Draft ellipse")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    result = draft_mod.draft_ellipse(
        proj,
        major_radius=major_radius,
        minor_radius=minor_radius,
        name=name,
        position=pos,
    )
    output_fn(result, f"Created ellipse: {result.get('name', '')}")


@draft_group.command("polygon")
@click.option("--sides", default=6, type=int)
@click.option("--radius", "-r", default=5.0, type=float)
@click.option("--name", "-n", help="Object name.")
@click.option("--position", "-pos", help="Position x,y,z.")
@handle_error
def draft_polygon(
    sides: int, radius: float, name: Optional[str], position: Optional[str]
) -> None:
    """Create a regular polygon."""
    sess = get_session()
    sess.snapshot("Draft polygon")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    result = draft_mod.draft_polygon(
        proj, sides=sides, radius=radius, name=name, position=pos
    )
    output_fn(result, f"Created polygon: {result.get('name', '')}")


@draft_group.command("bspline")
@click.argument("points_str", type=str)
@click.option("--closed", is_flag=True, help="Close the spline.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_bspline(points_str: str, closed: bool, name: Optional[str]) -> None:
    """Create a B-spline from semicolon-separated x,y,z points."""
    sess = get_session()
    sess.snapshot("Draft bspline")
    proj = sess.get_project()
    pts = _parse_points(points_str)
    result = draft_mod.draft_bspline(proj, points=pts, closed=closed, name=name)
    output_fn(result, f"Created B-spline: {result.get('name', '')}")


@draft_group.command("bezier")
@click.argument("points_str", type=str)
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_bezier(points_str: str, name: Optional[str]) -> None:
    """Create a Bezier curve from semicolon-separated x,y,z control points."""
    sess = get_session()
    sess.snapshot("Draft bezier")
    proj = sess.get_project()
    pts = _parse_points(points_str)
    result = draft_mod.draft_bezier(proj, points=pts, name=name)
    output_fn(result, f"Created Bezier: {result.get('name', '')}")


@draft_group.command("point")
@click.option("--point", "-p", default="0,0,0", help="Point x,y,z.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_point(point: str, name: Optional[str]) -> None:
    """Create a draft point."""
    sess = get_session()
    sess.snapshot("Draft point")
    proj = sess.get_project()
    pt = _parse_vec3(point)
    result = draft_mod.draft_point(proj, point=pt, name=name)
    output_fn(result, f"Created point: {result.get('name', '')}")
