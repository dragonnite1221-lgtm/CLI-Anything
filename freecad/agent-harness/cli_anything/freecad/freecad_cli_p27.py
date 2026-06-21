# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_points, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p26 import mesh_group  # noqa: E402,E501
# fmt: on


@mesh_group.command("remesh")
@click.argument("mesh_index", type=int)
@click.option("--target-length", default=1.0, type=float, help="Target edge length.")
@handle_error
def mesh_remesh(mesh_index: int, target_length: float) -> None:
    """Remesh with uniform edge lengths."""
    sess = get_session()
    sess.snapshot(f"Remesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.remesh_mesh(proj, mesh_index, target_length=target_length)
    output_fn(result, "Remeshed")


@mesh_group.command("smooth")
@click.argument("mesh_index", type=int)
@click.option("--iterations", default=3, type=int, help="Smoothing passes.")
@click.option("--factor", default=0.5, type=float, help="Smoothing factor (0-1).")
@handle_error
def mesh_smooth(mesh_index: int, iterations: int, factor: float) -> None:
    """Smooth a mesh."""
    sess = get_session()
    sess.snapshot(f"Smooth mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.smooth_mesh(
        proj, mesh_index, iterations=iterations, factor=factor
    )
    output_fn(result, "Smoothed mesh")


@mesh_group.command("repair")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_repair(mesh_index: int) -> None:
    """Repair a mesh."""
    sess = get_session()
    sess.snapshot(f"Repair mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.repair_mesh(proj, mesh_index)
    output_fn(result, "Repaired mesh")


@mesh_group.command("fill-holes")
@click.argument("mesh_index", type=int)
@click.option("--max-hole-size", default=10, type=int, help="Max hole size (edges).")
@handle_error
def mesh_fill_holes(mesh_index: int, max_hole_size: int) -> None:
    """Fill holes in a mesh."""
    sess = get_session()
    sess.snapshot(f"Fill holes mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.fill_holes(proj, mesh_index, max_hole_size=max_hole_size)
    output_fn(result, "Filled holes")


@mesh_group.command("flip-normals")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_flip_normals(mesh_index: int) -> None:
    """Flip all face normals."""
    sess = get_session()
    sess.snapshot(f"Flip normals mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.flip_normals(proj, mesh_index)
    output_fn(result, "Flipped normals")


@mesh_group.command("merge")
@click.argument("indices", type=str)
@click.option("--name", "-n", help="Name for merged mesh.")
@handle_error
def mesh_merge(indices: str, name: Optional[str]) -> None:
    """Merge multiple meshes (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Merge meshes")
    proj = sess.get_project()
    idx_list = _parse_indices(indices)
    result = mesh_mod.merge_meshes(proj, idx_list, name=name)
    output_fn(result, f"Merged mesh: {result.get('name', '')}")


@mesh_group.command("split")
@click.argument("mesh_index", type=int)
@handle_error
def mesh_split(mesh_index: int) -> None:
    """Split a mesh into disconnected components."""
    sess = get_session()
    sess.snapshot(f"Split mesh #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.split_mesh(proj, mesh_index)
    output_fn(result, "Split mesh")


@mesh_group.command("to-shape")
@click.argument("mesh_index", type=int)
@click.option("--name", "-n", help="Name for resulting part.")
@handle_error
def mesh_to_shape(mesh_index: int, name: Optional[str]) -> None:
    """Convert a mesh to a solid shape."""
    sess = get_session()
    sess.snapshot(f"Mesh to shape #{mesh_index}")
    proj = sess.get_project()
    result = mesh_mod.mesh_to_shape(proj, mesh_index, name=name)
    output_fn(result, f"Converted: {result.get('name', '')}")


@cli.group("draft")
def draft_group():
    """2D drafting commands."""
    pass


@draft_group.command("wire")
@click.argument("points_str", type=str)
@click.option("--closed", is_flag=True, help="Close the wire.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_wire(points_str: str, closed: bool, name: Optional[str]) -> None:
    """Create a wire from semicolon-separated x,y,z points."""
    sess = get_session()
    sess.snapshot("Draft wire")
    proj = sess.get_project()
    pts = _parse_points(points_str)
    result = draft_mod.draft_wire(proj, points=pts, closed=closed, name=name)
    output_fn(result, f"Created wire: {result.get('name', '')}")
