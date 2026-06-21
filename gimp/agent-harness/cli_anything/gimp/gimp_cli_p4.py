# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403

# fmt: off
from .gimp_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .gimp_cli_p3 import layer  # noqa: E402,E501
# fmt: on


@layer.command("flatten")
@handle_error
def layer_flatten():
    """Flatten all visible layers."""
    sess = get_session()
    sess.snapshot("Flatten layers")
    layer_mod.flatten_layers(sess.get_project())
    output(
        {"status": "flatten_pending"},
        "Layers marked for flattening (applied on export)",
    )


@layer.command("merge-down")
@click.argument("index", type=int)
@handle_error
def layer_merge_down(index):
    """Merge a layer with the one below it."""
    sess = get_session()
    sess.snapshot(f"Merge down layer {index}")
    layer_mod.merge_down(sess.get_project(), index)
    output(
        {"status": "merge_pending", "layer": index},
        f"Layer {index} marked for merge-down (applied on export)",
    )


@cli.group()
def canvas():
    """Canvas operations."""
    pass


@canvas.command("info")
@handle_error
def canvas_info():
    """Show canvas information."""
    sess = get_session()
    info = canvas_mod.get_canvas_info(sess.get_project())
    output(info)


@canvas.command("resize")
@click.option("--width", "-w", type=int, required=True)
@click.option("--height", "-h", type=int, required=True)
@click.option(
    "--anchor",
    default="center",
    help="Anchor: center, top-left, top-right, bottom-left, bottom-right, top, bottom, left, right",
)
@handle_error
def canvas_resize(width, height, anchor):
    """Resize the canvas (without scaling content)."""
    sess = get_session()
    sess.snapshot(f"Resize canvas to {width}x{height}")
    result = canvas_mod.resize_canvas(sess.get_project(), width, height, anchor)
    output(result, f"Canvas resized to {width}x{height}")


@canvas.command("scale")
@click.option("--width", "-w", type=int, required=True)
@click.option("--height", "-h", type=int, required=True)
@click.option(
    "--resample",
    default="lanczos",
    type=click.Choice(["nearest", "bilinear", "bicubic", "lanczos"]),
)
@handle_error
def canvas_scale(width, height, resample):
    """Scale the canvas and all content proportionally."""
    sess = get_session()
    sess.snapshot(f"Scale canvas to {width}x{height}")
    result = canvas_mod.scale_canvas(sess.get_project(), width, height, resample)
    output(result, f"Canvas scaled to {width}x{height}")


@canvas.command("crop")
@click.option("--left", "-l", type=int, required=True)
@click.option("--top", "-t", type=int, required=True)
@click.option("--right", "-r", type=int, required=True)
@click.option("--bottom", "-b", type=int, required=True)
@handle_error
def canvas_crop(left, top, right, bottom):
    """Crop the canvas to a rectangle."""
    sess = get_session()
    sess.snapshot(f"Crop canvas ({left},{top})-({right},{bottom})")
    result = canvas_mod.crop_canvas(sess.get_project(), left, top, right, bottom)
    output(result, "Canvas cropped")


@canvas.command("mode")
@click.argument("mode", type=click.Choice(["RGB", "RGBA", "L", "LA", "CMYK", "P"]))
@handle_error
def canvas_mode(mode):
    """Set the canvas color mode."""
    sess = get_session()
    sess.snapshot(f"Change mode to {mode}")
    result = canvas_mod.set_mode(sess.get_project(), mode)
    output(result, f"Canvas mode changed to {mode}")


@canvas.command("dpi")
@click.argument("dpi", type=int)
@handle_error
def canvas_dpi(dpi):
    """Set the canvas DPI."""
    sess = get_session()
    result = canvas_mod.set_dpi(sess.get_project(), dpi)
    output(result, f"DPI set to {dpi}")


@cli.group("filter")
def filter_group():
    """Filter management commands."""
    pass


@filter_group.command("list-available")
@click.option(
    "--category",
    "-c",
    type=str,
    default=None,
    help="Filter by category: adjustment, blur, stylize, transform",
)
@handle_error
def filter_list_available(category):
    """List all available filters."""
    filters = filt_mod.list_available(category)
    output(filters, "Available filters:")


@filter_group.command("info")
@click.argument("name")
@handle_error
def filter_info(name):
    """Show details about a filter."""
    info = filt_mod.get_filter_info(name)
    output(info)


@filter_group.command("add")
@click.argument("name")
@click.option("--layer", "-l", "layer_index", type=int, default=0, help="Layer index")
@click.option("--param", "-p", multiple=True, help="Parameter: key=value")
@handle_error
def filter_add(name, layer_index, param):
    """Add a filter to a layer."""
    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Invalid param format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        params[k] = v

    sess = get_session()
    sess.snapshot(f"Add filter {name} to layer {layer_index}")
    result = filt_mod.add_filter(sess.get_project(), name, layer_index, params)
    output(result, f"Added filter: {name}")
