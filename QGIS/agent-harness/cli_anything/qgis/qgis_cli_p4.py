# ruff: noqa: F403, F405, E501
from .qgis_cli_base import *  # noqa: F403

# fmt: off
from .qgis_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .qgis_cli_p2 import _auto_save_if_one_shot, _load_requested_project, _record  # noqa: E402,E501
from .qgis_cli_p3 import layout  # noqa: E402,E501
# fmt: on


@layout.command("create")
@click.option("--name", required=True, help="Layout name")
@click.option("--page-size", default="A4", show_default=True, help="Page size")
@click.option(
    "--orientation",
    default="portrait",
    show_default=True,
    type=click.Choice(["portrait", "landscape"], case_sensitive=False),
    help="Page orientation",
)
@handle_error
def layout_create(name: str, page_size: str, orientation: str):
    """Create a print layout."""
    _load_requested_project(required=True)
    data = layouts_mod.create_layout(name, page_size=page_size, orientation=orientation)
    _auto_save_if_one_shot()
    _record(
        "layout create",
        {"name": name, "page_size": page_size, "orientation": orientation},
        data,
    )
    output(data, f"Created layout: {name}")


@layout.command("list")
@handle_error
def layout_list():
    """List print layouts in the current project."""
    _load_requested_project(required=True)
    data = layouts_mod.list_layouts()
    _record("layout list", {}, data)
    output(data)


@layout.command("info")
@click.argument("name")
@handle_error
def layout_info(name: str):
    """Show detailed information for a print layout."""
    _load_requested_project(required=True)
    data = layouts_mod.layout_info(name)
    _record("layout info", {"name": name}, data)
    output(data)


@layout.command("remove")
@click.argument("name")
@handle_error
def layout_remove(name: str):
    """Remove a print layout from the project."""
    _load_requested_project(required=True)
    data = layouts_mod.remove_layout(name)
    _auto_save_if_one_shot()
    _record("layout remove", {"name": name}, data)
    output(data, f"Removed layout: {name}")


@layout.command("add-map")
@click.option("--layout", "layout_name", required=True, help="Layout name")
@click.option("--x", type=float, required=True, help="Left position in millimeters")
@click.option("--y", type=float, required=True, help="Top position in millimeters")
@click.option("--width", type=float, required=True, help="Item width in millimeters")
@click.option("--height", type=float, required=True, help="Item height in millimeters")
@click.option("--extent", default=None, help="Map extent as xmin,ymin,xmax,ymax")
@handle_error
def layout_add_map(
    layout_name: str,
    x: float,
    y: float,
    width: float,
    height: float,
    extent: str | None,
):
    """Add a map item to a print layout."""
    _load_requested_project(required=True)
    data = layouts_mod.add_map_item(layout_name, x, y, width, height, extent=extent)
    _auto_save_if_one_shot()
    _record(
        "layout add-map",
        {
            "layout": layout_name,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "extent": extent,
        },
        data,
    )
    output(data, f"Added map item to layout: {layout_name}")


@layout.command("add-label")
@click.option("--layout", "layout_name", required=True, help="Layout name")
@click.option("--text", required=True, help="Label text")
@click.option("--x", type=float, required=True, help="Left position in millimeters")
@click.option("--y", type=float, required=True, help="Top position in millimeters")
@click.option("--width", type=float, required=True, help="Item width in millimeters")
@click.option("--height", type=float, required=True, help="Item height in millimeters")
@click.option(
    "--font-size", default=18.0, show_default=True, type=float, help="Font size"
)
@handle_error
def layout_add_label(
    layout_name: str,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_size: float,
):
    """Add a label item to a print layout."""
    _load_requested_project(required=True)
    data = layouts_mod.add_label_item(
        layout_name, text, x, y, width, height, font_size=font_size
    )
    _auto_save_if_one_shot()
    _record(
        "layout add-label",
        {
            "layout": layout_name,
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "font_size": font_size,
        },
        data,
    )
    output(data, f"Added label item to layout: {layout_name}")


@cli.group()
def export():
    """Layout export commands."""


@export.command("presets")
@handle_error
def export_presets():
    """List supported export formats and their backend algorithms."""
    data = export_mod.export_presets()
    _record("export presets", {}, data)
    output(data)
