# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p27 import draft_group  # noqa: E402,E501
# fmt: on


@draft_group.command("remove")
@click.argument("index", type=int)
@handle_error
def draft_remove(index: int) -> None:
    """Remove a draft object."""
    sess = get_session()
    sess.snapshot(f"Remove draft #{index}")
    proj = sess.get_project()
    result = draft_mod.remove_draft_object(proj, index)
    output_fn(result, f"Removed: {result.get('name', f'#{index}')}")


@cli.group("surface")
def surface_group():
    """Surface workbench commands."""
    pass


@surface_group.command("filling")
@click.argument("edge_indices", type=str)
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_filling(edge_indices: str, name: Optional[str]) -> None:
    """Create a filling surface from edge indices (comma-separated)."""
    sess = get_session()
    sess.snapshot("Surface filling")
    proj = sess.get_project()
    idx_list = _parse_indices(edge_indices)
    result = surface_mod.surface_filling(proj, edge_indices=idx_list, name=name)
    output_fn(result, f"Created filling: {result.get('name', '')}")


@surface_group.command("sections")
@click.argument("section_indices", type=str)
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_sections(section_indices: str, name: Optional[str]) -> None:
    """Create a loft surface through sections (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Surface sections")
    proj = sess.get_project()
    idx_list = _parse_indices(section_indices)
    result = surface_mod.surface_sections(proj, section_indices=idx_list, name=name)
    output_fn(result, f"Created sections: {result.get('name', '')}")


@surface_group.command("extend")
@click.argument("surface_index", type=int)
@click.option("--length", "-l", default=10.0, type=float, help="Extension length.")
@click.option("--direction", default="normal", type=click.Choice(["normal", "u", "v"]))
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_extend(
    surface_index: int, length: float, direction: str, name: Optional[str]
) -> None:
    """Extend a surface."""
    sess = get_session()
    sess.snapshot(f"Extend surface #{surface_index}")
    proj = sess.get_project()
    result = surface_mod.surface_extend(
        proj, surface_index, length=length, direction=direction, name=name
    )
    output_fn(result, f"Extended: {result.get('name', '')}")


@surface_group.command("blend-curve")
@click.argument("edge_index1", type=int)
@click.argument("edge_index2", type=int)
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_blend_curve(
    edge_index1: int, edge_index2: int, name: Optional[str]
) -> None:
    """Create a blend surface between two edges."""
    sess = get_session()
    sess.snapshot("Surface blend curve")
    proj = sess.get_project()
    result = surface_mod.surface_blend_curve(proj, edge_index1, edge_index2, name=name)
    output_fn(result, f"Created blend: {result.get('name', '')}")


@surface_group.command("sew")
@click.argument("surface_indices", type=str)
@click.option("--tolerance", default=0.01, type=float, help="Sewing tolerance.")
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_sew(surface_indices: str, tolerance: float, name: Optional[str]) -> None:
    """Sew surfaces together (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Surface sew")
    proj = sess.get_project()
    idx_list = _parse_indices(surface_indices)
    result = surface_mod.surface_sew(
        proj, surface_indices=idx_list, tolerance=tolerance, name=name
    )
    output_fn(result, f"Sewn: {result.get('name', '')}")


@surface_group.command("cut")
@click.argument("surface_index", type=int)
@click.argument("cutting_index", type=int)
@click.option("--name", "-n", help="Surface name.")
@handle_error
def surface_cut(surface_index: int, cutting_index: int, name: Optional[str]) -> None:
    """Cut a surface with another surface."""
    sess = get_session()
    sess.snapshot(f"Surface cut #{surface_index}")
    proj = sess.get_project()
    result = surface_mod.surface_cut(proj, surface_index, cutting_index, name=name)
    output_fn(result, f"Cut: {result.get('name', '')}")


@cli.group("import")
def import_group():
    """File import commands."""
    pass
