# ruff: noqa: F403, F405, E501
from .krita_cli_base import *  # noqa: F403

# fmt: off
from .krita_cli_p1 import _load_project, _output, _save_current, cli, handle_error  # noqa: E402,E501
from .krita_cli_p3 import layer  # noqa: E402,E501
# fmt: on


@layer.command("set")
@click.argument("layer_name")
@click.argument("property_name")
@click.argument("value")
@click.pass_context
@handle_error
def layer_set(ctx, layer_name, property_name, value):
    """Set a property on a layer (opacity, visible, blending_mode, locked)."""
    proj = _load_project(ctx)
    # Try to parse value as int or bool
    if value.lower() in ("true", "yes"):
        value = True
    elif value.lower() in ("false", "no"):
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            pass
    set_layer_property(proj, layer_name, property_name, value)
    _session.snapshot(proj, f"Set {property_name}={value} on layer '{layer_name}'")
    _save_current(ctx)
    _output(
        {
            "status": "updated",
            "layer": layer_name,
            "property": property_name,
            "value": value,
        },
        ctx,
    )


@cli.group()
@click.pass_context
def filter(ctx):
    """Apply filters and effects."""
    pass


@filter.command("apply")
@click.argument("filter_name")
@click.option(
    "-l",
    "--layer",
    "layer_name",
    default=None,
    help="Target layer name (default: top layer).",
)
@click.option(
    "-c", "--config", "config_json", default=None, help="Filter config as JSON string."
)
@click.pass_context
@handle_error
def filter_apply(ctx, filter_name, layer_name, config_json):
    """Apply a filter to a layer."""
    proj = _load_project(ctx)
    config = json.loads(config_json) if config_json else None
    if layer_name is None and proj.get("layers"):
        layer_name = proj["layers"][-1]["name"]
    add_filter(proj, layer_name, filter_name, config)
    _session.snapshot(proj, f"Applied filter '{filter_name}' to '{layer_name}'")
    _save_current(ctx)
    _output({"status": "applied", "filter": filter_name, "layer": layer_name}, ctx)


@filter.command("list")
@click.pass_context
@handle_error
def filter_list(ctx):
    """List available filters."""
    filters = [
        "blur",
        "gaussian-blur",
        "motion-blur",
        "lens-blur",
        "sharpen",
        "unsharp-mask",
        "brightness-contrast",
        "levels",
        "curves",
        "hue-saturation",
        "color-balance",
        "desaturate",
        "invert",
        "posterize",
        "threshold",
        "auto-contrast",
        "normalize",
        "emboss",
        "edge-detection",
        "oil-paint",
        "pixelize",
        "noise-reduction",
        "halftone",
    ]
    if ctx.obj.get("json"):
        click.echo(json.dumps({"filters": filters}))
    else:
        click.echo("Available filters:")
        for f in filters:
            click.echo(f"  - {f}")


@cli.group()
@click.pass_context
def canvas(ctx):
    """Canvas and image operations."""
    pass


@canvas.command("resize")
@click.option("-w", "--width", type=int, default=None, help="New width.")
@click.option("-h", "--height", type=int, default=None, help="New height.")
@click.option("--resolution", type=int, default=None, help="New DPI resolution.")
@click.pass_context
@handle_error
def canvas_resize(ctx, width, height, resolution):
    """Resize the canvas."""
    proj = _load_project(ctx)
    set_canvas(proj, width=width, height=height, resolution=resolution)
    _session.snapshot(proj, f"Resized canvas to {width or '?'}x{height or '?'}")
    _save_current(ctx)
    info = proj["canvas"]
    _output(
        {
            "status": "resized",
            "width": info["width"],
            "height": info["height"],
            "resolution": info["resolution"],
        },
        ctx,
    )


@canvas.command("info")
@click.pass_context
@handle_error
def canvas_info(ctx):
    """Show canvas information."""
    proj = _load_project(ctx)
    _output(proj["canvas"], ctx)


@cli.group("export")
@click.pass_context
def export_group(ctx):
    """Export and render operations."""
    pass


@export_group.command("render")
@click.argument("output_path", type=click.Path())
@click.option(
    "-p",
    "--preset",
    default="png",
    type=click.Choice(list(EXPORT_PRESETS.keys())),
    help="Export preset.",
)
@click.option(
    "--overwrite", is_flag=True, default=False, help="Overwrite existing file."
)
@click.pass_context
@handle_error
def export_render(ctx, output_path, preset, overwrite):
    """Export/render the project to a file."""
    proj = _load_project(ctx)
    result = export_image(proj, output_path, preset=preset, overwrite=overwrite)
    _output(result, ctx)
