# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403

# fmt: off
from .drawio_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .drawio_cli_p3 import cli, shape  # noqa: E402,E501
# fmt: on


@shape.command("add")
@click.argument("shape_type", default="rectangle")
@click.option("--label", "-l", default="", help="Text label")
@click.option("--x", type=float, default=100, help="X position")
@click.option("--y", type=float, default=100, help="Y position")
@click.option("--width", "-w", type=float, default=120, help="Width")
@click.option("--height", "-h", type=float, default=60, help="Height")
@click.option("--page", type=int, default=0, help="Page index")
@click.option(
    "--id", "cell_id", default=None, help="Custom cell ID (auto-generated if omitted)"
)
@handle_error
def shape_add(shape_type, label, x, y, width, height, page, cell_id):
    """Add a shape to the diagram.

    SHAPE_TYPE: rectangle, rounded, ellipse, diamond, triangle, hexagon,
    cylinder, cloud, parallelogram, process, document, callout, note, actor, text
    """
    session = get_session()
    result = shapes_mod.add_shape(
        session, shape_type, x, y, width, height, label, page, cell_id
    )
    output(result, f"Added {shape_type}: {result['id']}")


@shape.command("remove")
@click.argument("cell_id")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_remove(cell_id, page):
    """Remove a shape by ID."""
    session = get_session()
    result = shapes_mod.remove_shape(session, cell_id, page)
    output(result, f"Removed: {cell_id}")


@shape.command("list")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_list(page):
    """List all shapes on a page."""
    session = get_session()
    result = shapes_mod.list_shapes(session, page)
    output(result, f"Shapes ({len(result)}):")


@shape.command("label")
@click.argument("cell_id")
@click.argument("label")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_label(cell_id, label, page):
    """Update a shape's label text."""
    session = get_session()
    result = shapes_mod.update_label(session, cell_id, label, page)
    output(result, f"Updated label: {cell_id}")


@shape.command("move")
@click.argument("cell_id")
@click.option("--x", type=float, required=True, help="New X position")
@click.option("--y", type=float, required=True, help="New Y position")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_move(cell_id, x, y, page):
    """Move a shape to new coordinates."""
    session = get_session()
    result = shapes_mod.move_shape(session, cell_id, x, y, page)
    output(result, f"Moved: {cell_id}")


@shape.command("resize")
@click.argument("cell_id")
@click.option("--width", "-w", type=float, required=True, help="New width")
@click.option("--height", "-h", type=float, required=True, help="New height")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_resize(cell_id, width, height, page):
    """Resize a shape."""
    session = get_session()
    result = shapes_mod.resize_shape(session, cell_id, width, height, page)
    output(result, f"Resized: {cell_id}")


@shape.command("style")
@click.argument("cell_id")
@click.argument("key")
@click.argument("value")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_style(cell_id, key, value, page):
    """Set a style property on a shape.

    Common keys: fillColor, strokeColor, fontColor, fontSize, opacity,
    rounded, shadow, dashed, strokeWidth
    """
    session = get_session()
    result = shapes_mod.set_style(session, cell_id, key, value, page)
    output(result, f"Style set: {key}={value}")


@shape.command("info")
@click.argument("cell_id")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def shape_info(cell_id, page):
    """Show detailed info about a shape."""
    session = get_session()
    result = shapes_mod.get_shape_info(session, cell_id, page)
    output(result)


@shape.command("types")
@handle_error
def shape_types():
    """List all available shape types."""
    result = shapes_mod.list_shape_types()
    output(result, "Shape types:")


@cli.group()
def connect():
    """Connector operations: add, remove, style."""
    pass


@connect.command("add")
@click.argument("source_id")
@click.argument("target_id")
@click.option(
    "--style",
    "edge_style",
    default="orthogonal",
    type=click.Choice(["straight", "orthogonal", "curved", "entity-relation"]),
    help="Edge style",
)
@click.option("--label", "-l", default="", help="Edge label")
@click.option("--page", type=int, default=0, help="Page index")
@click.option(
    "--id", "edge_id", default=None, help="Custom edge ID (auto-generated if omitted)"
)
@handle_error
def connect_add(source_id, target_id, edge_style, label, page, edge_id):
    """Add a connector between two shapes."""
    session = get_session()
    result = conn_mod.add_connector(
        session, source_id, target_id, edge_style, label, page, edge_id
    )
    output(result, f"Connected: {source_id} → {target_id}")


@connect.command("remove")
@click.argument("edge_id")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def connect_remove(edge_id, page):
    """Remove a connector by ID."""
    session = get_session()
    result = conn_mod.remove_connector(session, edge_id, page)
    output(result, f"Removed connector: {edge_id}")


@connect.command("label")
@click.argument("edge_id")
@click.argument("label")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def connect_label(edge_id, label, page):
    """Update a connector's label."""
    session = get_session()
    result = conn_mod.update_connector_label(session, edge_id, label, page)
    output(result, f"Updated label: {edge_id}")


@connect.command("style")
@click.argument("edge_id")
@click.argument("key")
@click.argument("value")
@click.option("--page", type=int, default=0, help="Page index")
@handle_error
def connect_style(edge_id, key, value, page):
    """Set a style property on a connector."""
    session = get_session()
    result = conn_mod.set_connector_style(session, edge_id, key, value, page)
    output(result, f"Style set: {key}={value}")
