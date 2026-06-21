# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p23 import session_group  # noqa: E402,E501
# fmt: on


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show session status."""
    sess = get_session()
    result = sess.status()
    output_fn(result, "Session status:")


@session_group.command("history")
@handle_error
def session_history() -> None:
    """Show undo history."""
    sess = get_session()
    result = sess.list_history()
    output_fn(result, f"{len(result)} history entries:")


@cli.group("measure")
def measure_group():
    """Measurement and geometry analysis commands."""
    pass


@measure_group.command("distance")
@click.argument("index1", type=int)
@click.argument("index2", type=int)
@handle_error
def measure_distance(index1: int, index2: int) -> None:
    """Measure distance between two parts."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_distance(proj, index1, index2)
    output_fn(result, f"Distance: {result.get('distance', 'N/A')}")


@measure_group.command("length")
@click.argument("index", type=int)
@click.option("--edge-ref", help="Edge reference (e.g. Edge1).")
@handle_error
def measure_length(index: int, edge_ref: Optional[str]) -> None:
    """Measure length of a part edge."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_length(proj, index, edge_ref=edge_ref)
    output_fn(result, f"Length: {result.get('length', 'N/A')}")


@measure_group.command("angle")
@click.argument("index1", type=int)
@click.argument("index2", type=int)
@handle_error
def measure_angle(index1: int, index2: int) -> None:
    """Measure angle between two parts."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_angle(proj, index1, index2)
    output_fn(result, f"Angle: {result.get('angle_deg', 'N/A')} deg")


@measure_group.command("area")
@click.argument("index", type=int)
@handle_error
def measure_area(index: int) -> None:
    """Measure surface area of a part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_area(proj, index)
    output_fn(result, f"Area: {result.get('area', 'N/A')}")


@measure_group.command("volume")
@click.argument("index", type=int)
@handle_error
def measure_volume(index: int) -> None:
    """Measure volume of a part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_volume(proj, index)
    output_fn(result, f"Volume: {result.get('volume', 'N/A')}")


@measure_group.command("radius")
@click.argument("index", type=int)
@handle_error
def measure_radius(index: int) -> None:
    """Measure radius of a cylindrical/spherical part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_radius(proj, index)
    output_fn(result, f"Radius: {result.get('radius', 'N/A')}")


@measure_group.command("diameter")
@click.argument("index", type=int)
@handle_error
def measure_diameter(index: int) -> None:
    """Measure diameter of a cylindrical/spherical part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_diameter(proj, index)
    output_fn(result, f"Diameter: {result.get('diameter', 'N/A')}")


@measure_group.command("position")
@click.argument("index", type=int)
@handle_error
def measure_position(index: int) -> None:
    """Get the position of a part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_position(proj, index)
    output_fn(result, f"Position: {result.get('position', 'N/A')}")


@measure_group.command("center-of-mass")
@click.argument("index", type=int)
@handle_error
def measure_center_of_mass(index: int) -> None:
    """Estimate center of mass of a part."""
    sess = get_session()
    proj = sess.get_project()
    result = measure_mod.measure_center_of_mass(proj, index)
    output_fn(result, f"Center of mass: {result.get('center_of_mass', 'N/A')}")
