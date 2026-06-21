# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p25 import spreadsheet_group  # noqa: E402,E501
# fmt: on


@spreadsheet_group.command("list")
@handle_error
def spreadsheet_list() -> None:
    """List all spreadsheets."""
    sess = get_session()
    proj = sess.get_project()
    result = spread_mod.list_spreadsheets(proj)
    output_fn(result, f"{len(result)} spreadsheet(s):")


@cli.group("mesh")
def mesh_group():
    """Mesh operations commands."""
    pass


@mesh_group.command("import")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def mesh_import(path: str, name: Optional[str]) -> None:
    """Import a mesh file."""
    sess = get_session()
    sess.snapshot("Import mesh")
    proj = sess.get_project()
    result = mesh_mod.import_mesh(proj, path, name=name)
    output_fn(result, f"Imported mesh: {result.get('name', '')}")


@mesh_group.command("from-shape")
@click.argument("part_index", type=int)
@click.option("--name", "-n", help="Mesh name.")
@click.option("--max-length", type=float, help="Max edge length.")
@click.option("--deviation", default=0.1, type=float, help="Surface deviation.")
@handle_error
def mesh_from_shape(
    part_index: int, name: Optional[str], max_length: Optional[float], deviation: float
) -> None:
    """Tessellate a part into a mesh."""
    sess = get_session()
    sess.snapshot(f"Mesh from shape #{part_index}")
    proj = sess.get_project()
    result = mesh_mod.mesh_from_shape(
        proj, part_index, name=name, max_length=max_length, deviation=deviation
    )
    output_fn(result, f"Created mesh: {result.get('name', '')}")


@mesh_group.command("export")
@click.argument("mesh_index", type=int)
@click.argument("path", type=click.Path())
@click.option("--format", "fmt", default="stl", help="Export format.")
@handle_error
def mesh_export(mesh_index: int, path: str, fmt: str) -> None:
    """Export a mesh to file."""
    sess = get_session()
    proj = sess.get_project()
    result = mesh_mod.export_mesh(proj, mesh_index, path, format=fmt)
    output_fn(result, f"Export mesh: {result.get('path', path)}")


@mesh_group.command("info")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_info(mesh_index: int) -> None:
    """Show mesh information."""
    sess = get_session()
    proj = sess.get_project()
    result = mesh_mod.mesh_info(proj, mesh_index)
    output_fn(result, f"Mesh #{mesh_index}:")


@mesh_group.command("analyze")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_analyze(mesh_index: int) -> None:
    """Analyze a mesh."""
    sess = get_session()
    proj = sess.get_project()
    result = mesh_mod.analyze_mesh(proj, mesh_index)
    output_fn(result, "Mesh analysis:")


@mesh_group.command("check")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_check(mesh_index: int) -> None:
    """Check a mesh for problems."""
    sess = get_session()
    proj = sess.get_project()
    result = mesh_mod.check_mesh(proj, mesh_index)
    output_fn(result, "Mesh check:")


@mesh_group.command("boolean")
@click.argument("op", type=click.Choice(["union", "difference", "intersection"]))
@click.argument("base_index", type=int)
@click.argument("tool_index", type=int)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def mesh_boolean(
    op: str, base_index: int, tool_index: int, name: Optional[str]
) -> None:
    """Perform boolean operation on two meshes."""
    sess = get_session()
    sess.snapshot(f"Mesh boolean {op}")
    proj = sess.get_project()
    result = mesh_mod.mesh_boolean(proj, op, base_index, tool_index, name=name)
    output_fn(result, f"Mesh boolean {op}: {result.get('name', '')}")


@mesh_group.command("decimate")
@click.argument("mesh_index", type=int)
@click.option("--target-faces", default=1000, type=int, help="Target face count.")
@handle_error
def mesh_decimate(mesh_index: int, target_faces: int) -> None:
    """Decimate (simplify) a mesh."""
    sess = get_session()
    sess.snapshot(f"Decimate mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.decimate_mesh(proj, mesh_index, target_faces=target_faces)
    output_fn(result, "Decimated mesh")
