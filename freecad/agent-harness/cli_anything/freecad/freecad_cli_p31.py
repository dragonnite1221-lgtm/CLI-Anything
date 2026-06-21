# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p27 import draft_group  # noqa: E402,E501
# fmt: on


@draft_group.command("clone")
@click.argument("index", type=int)
@click.option("--name", "-n", help="Name for clone.")
@handle_error
def draft_clone(index: int, name: Optional[str]) -> None:
    """Create a clone (linked copy) of a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft clone #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_clone(proj, index, name=name)
    output_fn(result, f"Cloned: {result.get('name', '')}")


@draft_group.command("upgrade")
@click.argument("index", type=int)
@handle_error
def draft_upgrade(index: int) -> None:
    """Upgrade a draft object (e.g. wires -> face)."""
    sess = get_session()
    sess.snapshot(f"Draft upgrade #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_upgrade(proj, index)
    output_fn(result, f"Upgraded: {result.get('name', '')}")


@draft_group.command("downgrade")
@click.argument("index", type=int)
@handle_error
def draft_downgrade(index: int) -> None:
    """Downgrade a draft object (e.g. face -> wires)."""
    sess = get_session()
    sess.snapshot(f"Draft downgrade #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_downgrade(proj, index)
    output_fn(result, f"Downgraded: {result.get('name', '')}")


@draft_group.command("trim")
@click.argument("index", type=int)
@click.argument("point", type=str)
@handle_error
def draft_trim(index: int, point: str) -> None:
    """Trim a draft object at a point (x,y,z)."""
    sess = get_session()
    sess.snapshot(f"Draft trim #{index}")
    proj = sess.get_project()
    pt = _parse_vec3(point)
    result = draft_mod.draft_trim(proj, index, point=pt)
    output_fn(result, f"Trimmed: {result.get('name', '')}")


@draft_group.command("join")
@click.argument("indices", type=str)
@click.option("--name", "-n", help="Name for joined result.")
@handle_error
def draft_join(indices: str, name: Optional[str]) -> None:
    """Join multiple draft wires (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Draft join")
    proj = sess.get_project()
    idx_list = _parse_indices(indices)
    result = draft_mod.draft_join(proj, indices=idx_list, name=name)
    output_fn(result, f"Joined: {result.get('name', '')}")


@draft_group.command("extrude")
@click.argument("index", type=int)
@click.option("--vector", "-v", help="Extrusion vector x,y,z.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def draft_extrude(index: int, vector: Optional[str], name: Optional[str]) -> None:
    """Extrude a 2D draft object into 3D."""
    sess = get_session()
    sess.snapshot(f"Draft extrude #{index}")
    proj = sess.get_project()
    vec = _parse_vec3(vector) if vector else None
    result = draft_mod.draft_extrude(proj, index, vector=vec, name=name)
    output_fn(result, f"Extruded: {result.get('name', '')}")


@draft_group.command("fillet-2d")
@click.argument("index", type=int)
@click.option("--radius", "-r", default=1.0, type=float, help="Fillet radius.")
@click.option(
    "--edges", default=None, type=str, help="Comma-separated edge indices to fillet."
)
@handle_error
def draft_fillet_2d(index: int, radius: float, edges: Optional[str]) -> None:
    """Apply a 2D fillet to a draft object."""
    sess = get_session()
    sess.snapshot(f"Draft fillet-2d #{index}")
    proj = sess.get_project()
    edge_list = [int(e) for e in edges.split(",")] if edges else None
    result = draft_mod.draft_fillet_2d(proj, index, radius=radius, edges=edge_list)
    output_fn(result, f"Fillet-2D: {result.get('name', '')}")


@draft_group.command("to-sketch")
@click.argument("index", type=int)
@click.option("--name", "-n", help="Name for resulting sketch.")
@handle_error
def draft_to_sketch(index: int, name: Optional[str]) -> None:
    """Convert a draft object to a sketch."""
    sess = get_session()
    sess.snapshot(f"Draft to sketch #{index}")
    proj = sess.get_project()
    result = draft_mod.draft_to_sketch(proj, index, name=name)
    output_fn(result, f"Converted to sketch: {result.get('name', '')}")


@draft_group.command("list")
@handle_error
def draft_list() -> None:
    """List all draft objects."""
    sess = get_session()
    proj = sess.get_project()
    result = draft_mod.list_draft_objects(proj)
    output_fn(result, f"{len(result)} draft object(s):")


@draft_group.command("get")
@click.argument("index", type=int)
@handle_error
def draft_get(index: int) -> None:
    """Get draft object details."""
    sess = get_session()
    proj = sess.get_project()
    result = draft_mod.get_draft_object(proj, index)
    output_fn(result, f"Draft object #{index}:")
