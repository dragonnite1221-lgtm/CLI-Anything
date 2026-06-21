# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_references, _parse_vec3, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p36 import techdraw_group  # noqa: E402,E501
# fmt: on


@techdraw_group.command("get-view")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@handle_error
def techdraw_get_view(page_index: int, view_index: int) -> None:
    """Get details of a specific view."""
    sess = get_session()
    proj = sess.get_project()
    result = td_mod.get_view(proj, page_index, view_index)
    output_fn(result, f"View #{view_index}:")


@cli.group("fem")
def fem_group():
    """FEM analysis commands."""
    pass


@fem_group.command("new-analysis")
@click.option("--name", "-n", help="Analysis name.")
@handle_error
def fem_new_analysis(name: Optional[str]) -> None:
    """Create a new FEM analysis."""
    sess = get_session()
    sess.snapshot("New FEM analysis")
    proj = sess.get_project()
    result = fem_mod.new_analysis(proj, name=name)
    output_fn(result, f"Created analysis: {result.get('name', '')}")


@fem_group.command("add-fixed")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@handle_error
def fem_add_fixed(ai: int, references: str) -> None:
    """Add a fixed boundary constraint."""
    sess = get_session()
    sess.snapshot(f"Add fixed constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = fem_mod.add_fixed_constraint(proj, ai, refs)
    output_fn(result, "Added fixed constraint")


@fem_group.command("add-force")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@click.option("--magnitude", "-m", required=True, type=float, help="Force in Newtons.")
@click.option("--direction", "-d", help="Direction x,y,z.")
@handle_error
def fem_add_force(
    ai: int, references: str, magnitude: float, direction: Optional[str]
) -> None:
    """Add a force constraint."""
    sess = get_session()
    sess.snapshot(f"Add force constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    d = _parse_vec3(direction) if direction else None
    result = fem_mod.add_force_constraint(proj, ai, refs, magnitude, direction=d)
    output_fn(result, "Added force constraint")


@fem_group.command("add-pressure")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@click.option("--pressure", "-p", required=True, type=float, help="Pressure in MPa.")
@handle_error
def fem_add_pressure(ai: int, references: str, pressure: float) -> None:
    """Add a pressure constraint."""
    sess = get_session()
    sess.snapshot(f"Add pressure constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = fem_mod.add_pressure_constraint(proj, ai, refs, pressure)
    output_fn(result, "Added pressure constraint")


@fem_group.command("add-displacement")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@click.option("--displacement", "-d", help="Displacement dx,dy,dz.")
@handle_error
def fem_add_displacement(ai: int, references: str, displacement: Optional[str]) -> None:
    """Add a displacement constraint."""
    sess = get_session()
    sess.snapshot(f"Add displacement constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    disp = _parse_vec3(displacement) if displacement else None
    result = fem_mod.add_displacement_constraint(proj, ai, refs, displacement=disp)
    output_fn(result, "Added displacement constraint")


@fem_group.command("add-temperature")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@click.option(
    "--temperature", "-t", required=True, type=float, help="Temperature in Kelvin."
)
@handle_error
def fem_add_temperature(ai: int, references: str, temperature: float) -> None:
    """Add a temperature constraint."""
    sess = get_session()
    sess.snapshot(f"Add temperature constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = fem_mod.add_temperature_constraint(proj, ai, refs, temperature)
    output_fn(result, "Added temperature constraint")


@fem_group.command("add-heatflux")
@click.argument("ai", type=int)
@click.option("--references", "-r", required=True, help="Geometry refs (comma-sep).")
@click.option("--flux", "-f", required=True, type=float, help="Heat flux in W/m^2.")
@handle_error
def fem_add_heatflux(ai: int, references: str, flux: float) -> None:
    """Add a heat flux constraint."""
    sess = get_session()
    sess.snapshot(f"Add heatflux constraint to analysis #{ai}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = fem_mod.add_heatflux_constraint(proj, ai, refs, flux)
    output_fn(result, "Added heat flux constraint")
