# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_points_2d, _parse_references, _parse_vec2, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p36 import techdraw_group  # noqa: E402,E501
# fmt: on


@techdraw_group.command("add-dimension")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@click.argument(
    "dim_type", type=click.Choice(["length", "distance", "radius", "diameter", "angle"])
)
@click.option(
    "--references", "-r", required=True, help="Geometry references (comma-sep)."
)
@click.option("--value", "-v", type=float, help="Override value.")
@handle_error
def techdraw_add_dimension(
    page_index: int,
    view_index: int,
    dim_type: str,
    references: str,
    value: Optional[float],
) -> None:
    """Add a dimension to a page."""
    sess = get_session()
    sess.snapshot(f"Add dimension to page #{page_index}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = td_mod.add_dimension(
        proj, page_index, view_index, dim_type, refs, value=value
    )
    output_fn(result, f"Added {dim_type} dimension")


@techdraw_group.command("add-annotation")
@click.argument("page_index", type=int)
@click.argument("text_content", type=str)
@click.option("--position", help="Position x,y.")
@click.option("--area", is_flag=True, help="Compute area accounting for face holes.")
@click.option(
    "--validate-shape", is_flag=True, default=False, help="Enable shape validation."
)
@handle_error
def techdraw_add_annotation(
    page_index: int,
    text_content: str,
    position: Optional[str],
    area: bool,
    validate_shape: bool,
) -> None:
    """Add a text annotation to a page."""
    sess = get_session()
    sess.snapshot(f"Add annotation to page #{page_index}")
    proj = sess.get_project()
    p = _parse_vec2(position) if position else None
    result = td_mod.add_annotation(
        proj,
        page_index,
        text_content,
        position=p,
        area_mode=area,
        shape_validation=validate_shape,
    )
    output_fn(result, "Added annotation")


@techdraw_group.command("add-leader")
@click.argument("page_index", type=int)
@click.argument("points_str", type=str)
@click.option("--text", "-t", default="", help="Leader text.")
@handle_error
def techdraw_add_leader(page_index: int, points_str: str, text: str) -> None:
    """Add a leader line (semicolon-separated x,y points)."""
    sess = get_session()
    sess.snapshot(f"Add leader to page #{page_index}")
    proj = sess.get_project()
    pts = _parse_points_2d(points_str)
    result = td_mod.add_leader(proj, page_index, points=pts, text=text)
    output_fn(result, "Added leader")


@techdraw_group.command("add-centerline")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@click.option("--references", "-r", required=True, help="References (comma-sep).")
@handle_error
def techdraw_add_centerline(page_index: int, view_index: int, references: str) -> None:
    """Add a centerline to a view."""
    sess = get_session()
    sess.snapshot(f"Add centerline to page #{page_index}")
    proj = sess.get_project()
    refs = _parse_references(references)
    result = td_mod.add_centerline(proj, page_index, view_index, references=refs)
    output_fn(result, "Added centerline")


@techdraw_group.command("add-hatch")
@click.argument("page_index", type=int)
@click.argument("view_index", type=int)
@click.option("--pattern", default="steel", help="Hatch pattern.")
@click.option("--scale", default=1.0, type=float, help="Pattern scale.")
@handle_error
def techdraw_add_hatch(
    page_index: int, view_index: int, pattern: str, scale: float
) -> None:
    """Add a hatch pattern to a view."""
    sess = get_session()
    sess.snapshot(f"Add hatch to page #{page_index}")
    proj = sess.get_project()
    result = td_mod.add_hatch(
        proj, page_index, view_index, pattern=pattern, scale=scale
    )
    output_fn(result, "Added hatch")


@techdraw_group.command("export-pdf")
@click.argument("page_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def techdraw_export_pdf(page_index: int, path: str) -> None:
    """Export a page to PDF."""
    sess = get_session()
    proj = sess.get_project()
    result = td_mod.export_page_pdf(proj, page_index, path)
    output_fn(result, f"Exported PDF: {path}")


@techdraw_group.command("export-svg")
@click.argument("page_index", type=int)
@click.argument("path", type=click.Path())
@handle_error
def techdraw_export_svg(page_index: int, path: str) -> None:
    """Export a page to SVG."""
    sess = get_session()
    proj = sess.get_project()
    result = td_mod.export_page_svg(proj, page_index, path)
    output_fn(result, f"Exported SVG: {path}")


@techdraw_group.command("list-views")
@click.argument("page_index", type=int)
@handle_error
def techdraw_list_views(page_index: int) -> None:
    """List all views on a page."""
    sess = get_session()
    proj = sess.get_project()
    result = td_mod.list_views(proj, page_index)
    output_fn(result, f"{len(result)} view(s):")
