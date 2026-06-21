# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p32 import import_group  # noqa: E402,E501
# fmt: on


@import_group.command("ply")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_ply(path: str, name: Optional[str]) -> None:
    """Import a PLY file."""
    sess = get_session()
    sess.snapshot("Import PLY")
    proj = sess.get_project()
    result = import_mod.import_ply(proj, path, name=name)
    output_fn(result, f"Imported PLY: {result.get('name', '')}")


@import_group.command("off")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_off(path: str, name: Optional[str]) -> None:
    """Import an OFF file."""
    sess = get_session()
    sess.snapshot("Import OFF")
    proj = sess.get_project()
    result = import_mod.import_off(proj, path, name=name)
    output_fn(result, f"Imported OFF: {result.get('name', '')}")


@import_group.command("gltf")
@click.argument("path", type=click.Path())
@click.option("--name", "-n", help="Mesh name.")
@handle_error
def import_gltf(path: str, name: Optional[str]) -> None:
    """Import a glTF/GLB file."""
    sess = get_session()
    sess.snapshot("Import glTF")
    proj = sess.get_project()
    result = import_mod.import_gltf(proj, path, name=name)
    output_fn(result, f"Imported glTF: {result.get('name', '')}")


@import_group.command("info")
@click.argument("path", type=click.Path())
@handle_error
def import_info(path: str) -> None:
    """Preview file metadata without importing."""
    result = import_mod.import_info(path)
    output_fn(result, "Import info:")


@cli.group("assembly")
def assembly_group():
    """Assembly management commands."""
    pass


@assembly_group.command("new")
@click.option("--name", "-n", help="Assembly name.")
@handle_error
def assembly_new(name: Optional[str]) -> None:
    """Create a new assembly."""
    sess = get_session()
    sess.snapshot("New assembly")
    proj = sess.get_project()
    result = asm_mod.create_assembly(proj, name=name)
    output_fn(result, f"Created assembly: {result.get('name', '')}")


@assembly_group.command("add-part")
@click.argument("asm_index", type=int)
@click.argument("part_index", type=int)
@click.option("--transform", help="Placement offset x,y,z.")
@handle_error
def assembly_add_part(
    asm_index: int, part_index: int, transform: Optional[str]
) -> None:
    """Add a part to an assembly."""
    sess = get_session()
    sess.snapshot(f"Add part #{part_index} to assembly #{asm_index}")
    proj = sess.get_project()
    t = _parse_vec3(transform) if transform else None
    result = asm_mod.add_part_to_assembly(proj, asm_index, part_index, transform=t)
    output_fn(result, f"Added: {result.get('name', '')}")


@assembly_group.command("remove-part")
@click.argument("asm_index", type=int)
@click.argument("component_index", type=int)
@handle_error
def assembly_remove_part(asm_index: int, component_index: int) -> None:
    """Remove a component from an assembly."""
    sess = get_session()
    sess.snapshot(f"Remove component #{component_index} from assembly #{asm_index}")
    proj = sess.get_project()
    result = asm_mod.remove_part_from_assembly(proj, asm_index, component_index)
    output_fn(result, f"Removed component #{component_index}")


@assembly_group.command("list")
@handle_error
def assembly_list() -> None:
    """List all assemblies."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.list_assemblies(proj)
    output_fn(result, f"{len(result)} assembly/assemblies:")


@assembly_group.command("get")
@click.argument("index", type=int)
@handle_error
def assembly_get(index: int) -> None:
    """Get assembly details."""
    sess = get_session()
    proj = sess.get_project()
    result = asm_mod.get_assembly(proj, index)
    output_fn(result, f"Assembly #{index}:")
