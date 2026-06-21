# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403

# fmt: off
from .drawio_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .drawio_cli_p3 import cli, page, session  # noqa: E402,E501
from .drawio_cli_p4 import connect  # noqa: E402,E501
# fmt: on


@connect.command("list")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def connect_list(page):
    """List all connectors on a page."""
    session = get_session()
    result = conn_mod.list_connectors(session, page)
    output(result, f"Connectors ({len(result)}):")


@connect.command("styles")
@handle_error
def connect_styles():
    """List available edge styles."""
    result = conn_mod.list_edge_styles()
    output(result, "Edge styles:")


@page.command("add")
@click.option("--name", default="", help="Page name")
@click.option("--width", type=int, default=850, help="Page width")
@click.option("--height", type=int, default=1100, help="Page height")
@handle_error
def page_add(name, width, height):
    """Add a new page."""
    session = get_session()
    result = pages_mod.add_page(session, name, width, height)
    output(result, f"Added page: {result['name']}")


@page.command("remove")
@click.argument("page_index", type=int)
@handle_error
def page_remove(page_index):
    """Remove a page by index."""
    session = get_session()
    result = pages_mod.remove_page(session, page_index)
    output(result, f"Removed page {page_index}")


@page.command("rename")
@click.argument("page_index", type=int)
@click.argument("name")
@handle_error
def page_rename(page_index, name):
    """Rename a page."""
    session = get_session()
    result = pages_mod.rename_page(session, page_index, name)
    output(result, f"Renamed page {page_index} to: {name}")


@page.command("list")
@handle_error
def page_list():
    """List all pages."""
    session = get_session()
    result = pages_mod.list_pages(session)
    output(result, f"Pages ({len(result)}):")


@cli.group()
def export():
    """Export operations: render to PNG, PDF, SVG."""
    pass


@export.command("render")
@click.argument("output_path")
@click.option(
    "--format",
    "-f",
    "fmt",
    default="png",
    type=click.Choice(["png", "pdf", "svg", "vsdx", "xml"]),
    help="Output format",
)
@click.option(
    "--page", "page_index", type=int, default=None, help="Page index to export"
)
@click.option("--scale", type=float, default=None, help="Scale factor")
@click.option("--width", type=int, default=None, help="Output width (PNG)")
@click.option("--height", type=int, default=None, help="Output height (PNG)")
@click.option("--transparent", is_flag=True, help="Transparent background (PNG)")
@click.option("--crop", is_flag=True, help="Crop to content")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@handle_error
def export_render(
    output_path, fmt, page_index, scale, width, height, transparent, crop, overwrite
):
    """Export the diagram to a file."""
    session = get_session()
    result = export_mod.render_or_save(
        session,
        output_path,
        fmt,
        page_index=page_index,
        scale=scale,
        width=width,
        height=height,
        transparent=transparent,
        crop=crop,
        overwrite=overwrite,
    )
    output(
        result, f"Exported to: {result.get('output', result.get('drawio_file', ''))}"
    )


@export.command("formats")
@handle_error
def export_formats():
    """List available export formats."""
    result = export_mod.list_formats()
    output(result, "Export formats:")


@session.command("status")
@handle_error
def session_status():
    """Show current session status."""
    s = get_session()
    result = s.status()
    output(result, "Session status:")


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    s = get_session()
    if s.undo():
        output({"action": "undo", "success": True}, "Undo successful")
    else:
        output({"action": "undo", "success": False}, "Nothing to undo")


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    s = get_session()
    if s.redo():
        output({"action": "redo", "success": True}, "Redo successful")
    else:
        output({"action": "redo", "success": False}, "Nothing to redo")


@session.command("save-state")
@handle_error
def session_save():
    """Save session state to disk."""
    s = get_session()
    path = s.save_session_state()
    output({"action": "save_session", "path": path}, f"Session saved: {path}")


@session.command("list")
@handle_error
def session_list():
    """List all saved sessions."""
    sessions = Session.list_sessions()
    output(sessions, f"Sessions ({len(sessions)}):")
