# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p27 import draft_group  # noqa: E402,E501
# fmt: on


@draft_group.command("text")
@click.argument("text_content", type=str)
@click.option("--name", "-n", help="Object name.")
@click.option("--position", "-pos", help="Position x,y,z.")
@handle_error
def draft_text(text_content: str, name: Optional[str], position: Optional[str]) -> None:
    """Create a text annotation."""
    sess = get_session()
    sess.snapshot("Draft text")
    proj = sess.get_project()
    pos = _parse_vec3(position) if position else None
    result = draft_mod.draft_text(proj, text=text_content, name=name, position=pos)
    output_fn(result, f"Created text: {result.get('name', '')}")


@draft_group.command("shapestring")
@click.argument("text_content", type=str)
@click.argument("font_file", type=str)
@click.option("--size", default=10.0, type=float, help="Font size.")
@click.option("--name", "-n", help="Object name.")
@click.option("--relative-font-path", is_flag=True, help="Use relative font path.")
@handle_error
def draft_shapestring(
    text_content: str,
    font_file: str,
    size: float,
    name: Optional[str],
    relative_font_path: bool,
) -> None:
    """Create a ShapeString."""
    sess = get_session()
    sess.snapshot("Draft shapestring")
    proj = sess.get_project()
    result = draft_mod.draft_shapestring(
        proj,
        text=text_content,
        font_file=font_file,
        size=size,
        name=name,
        font_path_relative=relative_font_path,
    )
    output_fn(result, f"Created shapestring: {result.get('name', '')}")


@draft_group.command("dimension")
@click.option("--start", "-s", required=True, help="Start point x,y,z.")
@click.option("--end", "-e", required=True, help="End point x,y,z.")
@click.option("--dim-line", help="Dimension line point x,y,z.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_dimension(
    start: str, end: str, dim_line: Optional[str], name: Optional[str]
) -> None:
    """Create a linear dimension annotation."""
    sess = get_session()
    sess.snapshot("Draft dimension")
    proj = sess.get_project()
    s = _parse_vec3(start)
    e = _parse_vec3(end)
    dl = _parse_vec3(dim_line) if dim_line else None
    result = draft_mod.draft_dimension(proj, start=s, end=e, dim_line=dl, name=name)
    output_fn(result, f"Created dimension: {result.get('name', '')}")


@draft_group.command("label")
@click.argument("target_point", type=str)
@click.option("--text", "-t", default="", help="Label text.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_label(target_point: str, text: str, name: Optional[str]) -> None:
    """Create a label pointing to a target point (x,y,z)."""
    sess = get_session()
    sess.snapshot("Draft label")
    proj = sess.get_project()
    tp = _parse_vec3(target_point)
    result = draft_mod.draft_label(proj, target_point=tp, text=text, name=name)
    output_fn(result, f"Created label: {result.get('name', '')}")


@draft_group.command("hatch")
@click.argument("target_index", type=int)
@click.option("--pattern", default="ANSI31", help="Hatch pattern.")
@click.option("--scale", default=1.0, type=float, help="Pattern scale.")
@click.option("--name", "-n", help="Object name.")
@handle_error
def draft_hatch(
    target_index: int, pattern: str, scale: float, name: Optional[str]
) -> None:
    """Apply a hatch pattern to a draft object."""
    sess = get_session()
    sess.snapshot("Draft hatch")
    proj = sess.get_project()
    result = draft_mod.draft_hatch(
        proj, target_index=target_index, pattern=pattern, scale=scale, name=name
    )
    output_fn(result, f"Created hatch: {result.get('name', '')}")


@draft_group.command("move")
@click.argument("index", type=int)
@click.argument("vector", type=str)
@click.option("--copy", is_flag=True, help="Create a moved copy.")
@handle_error
def draft_move(index: int, vector: str, copy: bool) -> None:
    """Move a draft object by a vector (x,y,z)."""
    sess = get_session()
    sess.snapshot(f"Draft move #{index}")
    proj = sess.get_project()
    vec = _parse_vec3(vector)
    result = draft_mod.draft_move(proj, index, vector=vec, copy=copy)
    output_fn(result, f"Moved: {result.get('name', '')}")


@draft_group.command("rotate")
@click.argument("index", type=int)
@click.argument("angle", type=float)
@click.option("--axis", help="Rotation axis x,y,z.")
@click.option("--center", help="Center of rotation x,y,z.")
@click.option("--copy", is_flag=True, help="Create a rotated copy.")
@handle_error
def draft_rotate(
    index: int, angle: float, axis: Optional[str], center: Optional[str], copy: bool
) -> None:
    """Rotate a draft object by angle degrees."""
    sess = get_session()
    sess.snapshot(f"Draft rotate #{index}")
    proj = sess.get_project()
    ax = _parse_vec3(axis) if axis else None
    ctr = _parse_vec3(center) if center else None
    result = draft_mod.draft_rotate(
        proj, index, angle=angle, axis=ax, center=ctr, copy=copy
    )
    output_fn(result, f"Rotated: {result.get('name', '')}")
