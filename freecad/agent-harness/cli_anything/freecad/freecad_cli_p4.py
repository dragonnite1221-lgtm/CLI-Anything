# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session, output  # noqa: E402,E501
from .freecad_cli_p2 import _parse_params, _parse_vec3, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p3 import document_group  # noqa: E402,E501
# fmt: on


@document_group.command("open")
@click.argument("path", type=click.Path(exists=True))
@handle_error
def document_open(path: str) -> None:
    """Open an existing document."""
    sess = get_session()
    proj = doc_mod.open_document(path)
    sess.set_project(proj, path=path)
    result = doc_mod.get_document_info(proj)
    output_fn(result, f"Opened: {path}")


@document_group.command("save")
@click.option("--output", "-o", type=click.Path(), help="Save to new path.")
@handle_error
def document_save(output: Optional[str]) -> None:
    """Save the current document."""
    sess = get_session()
    proj = sess.get_project()
    path = sess.save_session(path=output)
    result = {"saved_to": path}
    output_fn(result, f"Saved: {path}")


@document_group.command("info")
@handle_error
def document_info() -> None:
    """Show document information."""
    sess = get_session()
    proj = sess.get_project()
    result = doc_mod.get_document_info(proj)
    output_fn(result, "Document info:")


@document_group.command("profiles")
@handle_error
def document_profiles() -> None:
    """List available document profiles."""
    result = doc_mod.list_profiles()
    output_fn(result, "Available profiles:")


@cli.group("part")
def part_group():
    """3D part/primitive management commands."""
    pass


@part_group.command("add")
@click.argument("part_type", default="box")
@click.option("--name", "-n", help="Part name.")
@click.option("--position", "-pos", help="Position as x,y,z (e.g. 0,0,0).")
@click.option("--rotation", "-rot", help="Rotation as x,y,z degrees.")
@click.option("--param", "-P", multiple=True, help="Param as key=value.")
@handle_error
def part_add(
    part_type: str,
    name: Optional[str],
    position: Optional[str],
    rotation: Optional[str],
    param: tuple,
) -> None:
    """Add a 3D primitive part (box, cylinder, sphere, cone, torus, wedge, helix, spiral, thread)."""
    sess = get_session()
    sess.snapshot(f"Add part: {part_type}")
    proj = sess.get_project()

    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    params = _parse_params(param)

    result = parts_mod.add_part(
        proj, part_type=part_type, name=name, position=pos, rotation=rot, params=params
    )
    output_fn(result, f"Added {part_type}: {result.get('name', '')}")


@part_group.command("remove")
@click.argument("index", type=int)
@handle_error
def part_remove(index: int) -> None:
    """Remove a part by index."""
    sess = get_session()
    sess.snapshot(f"Remove part #{index}")
    proj = sess.get_project()
    result = parts_mod.remove_part(proj, index)
    output_fn(result, f"Removed: {result.get('name', f'#{index}')}")


@part_group.command("list")
@handle_error
def part_list() -> None:
    """List all parts."""
    sess = get_session()
    proj = sess.get_project()
    result = parts_mod.list_parts(proj)
    output_fn(result, f"{len(result)} part(s):")


@part_group.command("get")
@click.argument("index", type=int)
@handle_error
def part_get(index: int) -> None:
    """Get details of a part by index."""
    sess = get_session()
    proj = sess.get_project()
    result = parts_mod.get_part(proj, index)
    output_fn(result, f"Part #{index}:")


@part_group.command("transform")
@click.argument("index", type=int)
@click.option("--position", "-pos", help="New position as x,y,z.")
@click.option("--rotation", "-rot", help="New rotation as x,y,z degrees.")
@handle_error
def part_transform(
    index: int, position: Optional[str], rotation: Optional[str]
) -> None:
    """Transform a part (position and/or rotation)."""
    sess = get_session()
    sess.snapshot(f"Transform part #{index}")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    rot = _parse_vec3(rotation) if rotation else None
    result = parts_mod.transform_part(proj, index, position=pos, rotation=rot)
    output_fn(result, f"Transformed: {result.get('name', f'#{index}')}")
