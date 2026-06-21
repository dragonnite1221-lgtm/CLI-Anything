# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p32 import import_group  # noqa: E402,E501
# fmt: on


@import_group.command("auto")
@click.argument("path", type=click.Path())
@click.option("--format", "fmt", help="Explicit format override.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def import_auto(path: str, fmt: Optional[str], name: Optional[str]) -> None:
    """Auto-detect and import a file."""
    sess = get_session()
    sess.snapshot("Import file")
    proj = sess.get_project()
    result = import_mod.import_file(proj, path, format=fmt, name=name)
    output_fn(result, f"Imported: {result.get('name', '')}")


@import_group.command("step")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Part name.")
@handle_error
def import_step(path: str, name: Optional[str]) -> None:
    """Import a STEP file."""
    sess = get_session()
    sess.snapshot("Import STEP")
    proj = sess.get_project()
    result = import_mod.import_step(proj, path, name=name)
    output_fn(result, f"Imported STEP: {result.get('name', '')}")


@import_group.command("iges")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Part name.")
@handle_error
def import_iges(path: str, name: Optional[str]) -> None:
    """Import an IGES file."""
    sess = get_session()
    sess.snapshot("Import IGES")
    proj = sess.get_project()
    result = import_mod.import_iges(proj, path, name=name)
    output_fn(result, f"Imported IGES: {result.get('name', '')}")


@import_group.command("stl")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_stl(path: str, name: Optional[str]) -> None:
    """Import an STL file."""
    sess = get_session()
    sess.snapshot("Import STL")
    proj = sess.get_project()
    result = import_mod.import_stl(proj, path, name=name)
    output_fn(result, f"Imported STL: {result.get('name', '')}")


@import_group.command("obj")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_obj(path: str, name: Optional[str]) -> None:
    """Import an OBJ file."""
    sess = get_session()
    sess.snapshot("Import OBJ")
    proj = sess.get_project()
    result = import_mod.import_obj(proj, path, name=name)
    output_fn(result, f"Imported OBJ: {result.get('name', '')}")


@import_group.command("dxf")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Object name.")
@handle_error
def import_dxf(path: str, name: Optional[str]) -> None:
    """Import a DXF file."""
    sess = get_session()
    sess.snapshot("Import DXF")
    proj = sess.get_project()
    result = import_mod.import_dxf(proj, path, name=name)
    output_fn(result, f"Imported DXF: {result.get('name', '')}")


@import_group.command("svg")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Object name.")
@handle_error
def import_svg(path: str, name: Optional[str]) -> None:
    """Import an SVG file."""
    sess = get_session()
    sess.snapshot("Import SVG")
    proj = sess.get_project()
    result = import_mod.import_svg(proj, path, name=name)
    output_fn(result, f"Imported SVG: {result.get('name', '')}")


@import_group.command("brep")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Part name.")
@handle_error
def import_brep(path: str, name: Optional[str]) -> None:
    """Import a BREP file."""
    sess = get_session()
    sess.snapshot("Import BREP")
    proj = sess.get_project()
    result = import_mod.import_brep(proj, path, name=name)
    output_fn(result, f"Imported BREP: {result.get('name', '')}")


@import_group.command("3mf")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_3mf(path: str, name: Optional[str]) -> None:
    """Import a 3MF file."""
    sess = get_session()
    sess.snapshot("Import 3MF")
    proj = sess.get_project()
    result = import_mod.import_3mf(proj, path, name=name)
    output_fn(result, f"Imported 3MF: {result.get('name', '')}")
