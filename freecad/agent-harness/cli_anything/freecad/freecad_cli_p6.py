# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p4 import part_group  # noqa: E402,E501
# fmt: on


@part_group.command("fillet-3d")
@click.argument("index", type=int)
@click.option("--radius", "-r", default=1.0, type=float, help="Fillet radius.")
@click.option("--edges", default="all", help="Edges: 'all' or comma-sep indices.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_fillet_3d(index: int, radius: float, edges: str, name: Optional[str]) -> None:
    """Apply a 3D fillet to a part."""
    sess = get_session()
    sess.snapshot(f"Fillet-3d part #{index}")
    proj = sess.get_project()
    result = parts_mod.fillet_3d(proj, index, radius=radius, edges=edges, name=name)
    output_fn(result, f"Fillet-3D: {result.get('name', '')}")


@part_group.command("chamfer-3d")
@click.argument("index", type=int)
@click.option("--size", "-s", default=1.0, type=float, help="Chamfer size.")
@click.option("--edges", default="all", help="Edges: 'all' or comma-sep indices.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_chamfer_3d(index: int, size: float, edges: str, name: Optional[str]) -> None:
    """Apply a 3D chamfer to a part."""
    sess = get_session()
    sess.snapshot(f"Chamfer-3d part #{index}")
    proj = sess.get_project()
    result = parts_mod.chamfer_3d(proj, index, size=size, edges=edges, name=name)
    output_fn(result, f"Chamfer-3D: {result.get('name', '')}")


@part_group.command("loft")
@click.argument("section_indices", type=str)
@click.option("--solid/--no-solid", default=True, help="Create solid.")
@click.option("--ruled", is_flag=True, help="Use ruled surfaces.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_loft(
    section_indices: str, solid: bool, ruled: bool, name: Optional[str]
) -> None:
    """Loft through cross-section parts (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Loft parts")
    proj = sess.get_project()
    idx_list = _parse_indices(section_indices)
    result = parts_mod.loft_parts(proj, idx_list, solid=solid, ruled=ruled, name=name)
    output_fn(result, f"Loft: {result.get('name', '')}")


@part_group.command("sweep")
@click.argument("profile_index", type=int)
@click.argument("path_index", type=int)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_sweep(profile_index: int, path_index: int, name: Optional[str]) -> None:
    """Sweep a profile shape along a path."""
    sess = get_session()
    sess.snapshot("Sweep part")
    proj = sess.get_project()
    result = parts_mod.sweep_part(proj, profile_index, path_index, name=name)
    output_fn(result, f"Sweep: {result.get('name', '')}")


@part_group.command("revolve")
@click.argument("index", type=int)
@click.option(
    "--axis", default="Z", type=click.Choice(["X", "Y", "Z"]), help="Revolution axis."
)
@click.option("--angle", "-a", default=360.0, type=float, help="Angle in degrees.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_revolve(index: int, axis: str, angle: float, name: Optional[str]) -> None:
    """Revolve a part around an axis."""
    sess = get_session()
    sess.snapshot(f"Revolve part #{index}")
    proj = sess.get_project()
    result = parts_mod.revolve_part(proj, index, axis=axis, angle=angle, name=name)
    output_fn(result, f"Revolve: {result.get('name', '')}")


@part_group.command("extrude")
@click.argument("index", type=int)
@click.option("--direction", "-d", help="Direction as x,y,z.")
@click.option("--length", "-l", default=10.0, type=float, help="Extrusion length.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_extrude(
    index: int, direction: Optional[str], length: float, name: Optional[str]
) -> None:
    """Extrude a part along a direction."""
    sess = get_session()
    sess.snapshot(f"Extrude part #{index}")
    proj = sess.get_project()
    dir_vec = _parse_vec3(direction) if direction else None
    result = parts_mod.extrude_part(
        proj, index, direction=dir_vec, length=length, name=name
    )
    output_fn(result, f"Extrude: {result.get('name', '')}")


@part_group.command("section")
@click.argument("index", type=int)
@click.option(
    "--plane",
    default="XY",
    type=click.Choice(["XY", "XZ", "YZ"]),
    help="Section plane.",
)
@click.option("--offset", default=0.0, type=float, help="Plane offset.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_section(index: int, plane: str, offset: float, name: Optional[str]) -> None:
    """Create a cross-section of a part."""
    sess = get_session()
    sess.snapshot(f"Section part #{index}")
    proj = sess.get_project()
    result = parts_mod.section_part(proj, index, plane=plane, offset=offset, name=name)
    output_fn(result, f"Section: {result.get('name', '')}")
