# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_indices, _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p4 import part_group  # noqa: E402,E501
# fmt: on


@part_group.command("boolean")
@click.argument("operation", type=click.Choice(["cut", "fuse", "common"]))
@click.argument("base_index", type=int)
@click.argument("tool_index", type=int)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_boolean(
    operation: str, base_index: int, tool_index: int, name: Optional[str]
) -> None:
    """Perform boolean operation (cut, fuse, common) on two parts."""
    sess = get_session()
    sess.snapshot(f"Boolean {operation}: #{base_index} vs #{tool_index}")
    proj = sess.get_project()
    result = parts_mod.boolean_op(proj, operation, base_index, tool_index, name=name)
    output_fn(result, f"Boolean {operation}: {result.get('name', '')}")


@part_group.command("copy")
@click.argument("index", type=int)
@click.option("--name", "-n", help="Name for copy.")
@handle_error
def part_copy(index: int, name: Optional[str]) -> None:
    """Copy a part by index."""
    sess = get_session()
    sess.snapshot(f"Copy part #{index}")
    proj = sess.get_project()
    result = parts_mod.copy_part(proj, index, name=name)
    output_fn(result, f"Copied: {result.get('name', '')}")


@part_group.command("mirror")
@click.argument("index", type=int)
@click.option(
    "--plane", default="XY", type=click.Choice(["XY", "XZ", "YZ"]), help="Mirror plane."
)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_mirror(index: int, plane: str, name: Optional[str]) -> None:
    """Create a mirrored copy of a part."""
    sess = get_session()
    sess.snapshot(f"Mirror part #{index}")
    proj = sess.get_project()
    result = parts_mod.mirror_part(proj, index, plane=plane, name=name)
    output_fn(result, f"Mirrored: {result.get('name', '')}")


@part_group.command("scale")
@click.argument("index", type=int)
@click.argument("factor", type=str)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_scale(index: int, factor: str, name: Optional[str]) -> None:
    """Scale a part by a uniform factor or x,y,z factors."""
    sess = get_session()
    sess.snapshot(f"Scale part #{index}")
    proj = sess.get_project()
    if "," in factor:
        fac = _parse_vec3(factor)
    else:
        fac = float(factor)
    result = parts_mod.scale_part(proj, index, factor=fac, name=name)
    output_fn(result, f"Scaled: {result.get('name', '')}")


@part_group.command("offset")
@click.argument("index", type=int)
@click.argument("distance", type=float)
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_offset(index: int, distance: float, name: Optional[str]) -> None:
    """Create an offset shell of a part."""
    sess = get_session()
    sess.snapshot(f"Offset part #{index}")
    proj = sess.get_project()
    result = parts_mod.offset_shape(proj, index, distance=distance, name=name)
    output_fn(result, f"Offset: {result.get('name', '')}")


@part_group.command("thickness")
@click.argument("index", type=int)
@click.argument("thickness_val", type=float)
@click.option("--faces", default="all", help="Faces: 'all' or comma-sep indices.")
@click.option("--name", "-n", help="Name for result.")
@handle_error
def part_thickness(
    index: int, thickness_val: float, faces: str, name: Optional[str]
) -> None:
    """Hollow a solid by applying wall thickness."""
    sess = get_session()
    sess.snapshot(f"Thickness part #{index}")
    proj = sess.get_project()
    result = parts_mod.thickness_part(
        proj, index, thickness=thickness_val, faces=faces, name=name
    )
    output_fn(result, f"Thickness: {result.get('name', '')}")


@part_group.command("compound")
@click.argument("indices", type=str)
@click.option("--name", "-n", help="Name for compound.")
@handle_error
def part_compound(indices: str, name: Optional[str]) -> None:
    """Group parts into a compound (comma-separated indices)."""
    sess = get_session()
    sess.snapshot("Create compound")
    proj = sess.get_project()
    idx_list = _parse_indices(indices)
    result = parts_mod.compound_parts(proj, idx_list, name=name)
    output_fn(result, f"Compound: {result.get('name', '')}")


@part_group.command("explode")
@click.argument("index", type=int)
@handle_error
def part_explode(index: int) -> None:
    """Explode a compound into individual parts."""
    sess = get_session()
    sess.snapshot(f"Explode compound #{index}")
    proj = sess.get_project()
    result = parts_mod.explode_compound(proj, index)
    output_fn(result, f"Exploded {len(result)} part(s)")
