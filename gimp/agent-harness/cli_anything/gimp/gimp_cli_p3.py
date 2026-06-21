# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403

# fmt: off
from .gimp_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .gimp_cli_p2 import project  # noqa: E402,E501
# fmt: on


@project.command("save")
@click.argument("path", required=False)
@handle_error
def project_save(path):
    """Save the current project."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@project.command("info")
@handle_error
def project_info():
    """Show project information."""
    sess = get_session()
    info = proj_mod.get_project_info(sess.get_project())
    output(info)


@project.command("profiles")
@handle_error
def project_profiles():
    """List available canvas profiles."""
    profiles = proj_mod.list_profiles()
    output(profiles, "Available profiles:")


@project.command("json")
@handle_error
def project_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group()
def layer():
    """Layer management commands."""
    pass


@layer.command("new")
@click.option("--name", "-n", default="New Layer", help="Layer name")
@click.option(
    "--type",
    "layer_type",
    type=click.Choice(["image", "text", "solid"]),
    default="image",
    help="Layer type",
)
@click.option("--width", "-w", type=int, default=None, help="Layer width")
@click.option("--height", "-h", type=int, default=None, help="Layer height")
@click.option(
    "--fill", default="transparent", help="Fill: transparent, white, black, or hex"
)
@click.option("--opacity", type=float, default=1.0, help="Layer opacity 0.0-1.0")
@click.option("--mode", default="normal", help="Blend mode")
@click.option("--position", "-p", type=int, default=None, help="Stack position (0=top)")
@handle_error
def layer_new(name, layer_type, width, height, fill, opacity, mode, position):
    """Create a new blank layer."""
    sess = get_session()
    sess.snapshot(f"Add layer: {name}")
    proj = sess.get_project()
    layer = layer_mod.add_layer(
        proj,
        name=name,
        layer_type=layer_type,
        width=width,
        height=height,
        fill=fill,
        opacity=opacity,
        blend_mode=mode,
        position=position,
    )
    output(layer, f"Added layer: {name}")


@layer.command("add-from-file")
@click.argument("path")
@click.option("--name", "-n", default=None, help="Layer name")
@click.option("--position", "-p", type=int, default=None, help="Stack position")
@click.option("--opacity", type=float, default=1.0, help="Layer opacity")
@click.option("--mode", default="normal", help="Blend mode")
@handle_error
def layer_add_from_file(path, name, position, opacity, mode):
    """Add a layer from an image file."""
    sess = get_session()
    sess.snapshot(f"Add layer from: {path}")
    proj = sess.get_project()
    layer = layer_mod.add_from_file(
        proj,
        path=path,
        name=name,
        position=position,
        opacity=opacity,
        blend_mode=mode,
    )
    output(layer, f"Added layer from: {path}")


@layer.command("list")
@handle_error
def layer_list():
    """List all layers."""
    sess = get_session()
    layers = layer_mod.list_layers(sess.get_project())
    output(layers, "Layers (top to bottom):")


@layer.command("remove")
@click.argument("index", type=int)
@handle_error
def layer_remove(index):
    """Remove a layer by index."""
    sess = get_session()
    sess.snapshot(f"Remove layer {index}")
    removed = layer_mod.remove_layer(sess.get_project(), index)
    output(removed, f"Removed layer {index}: {removed.get('name', '')}")


@layer.command("duplicate")
@click.argument("index", type=int)
@handle_error
def layer_duplicate(index):
    """Duplicate a layer."""
    sess = get_session()
    sess.snapshot(f"Duplicate layer {index}")
    dup = layer_mod.duplicate_layer(sess.get_project(), index)
    output(dup, f"Duplicated layer {index}")


@layer.command("move")
@click.argument("index", type=int)
@click.option("--to", type=int, required=True, help="Target position")
@handle_error
def layer_move(index, to):
    """Move a layer to a new position."""
    sess = get_session()
    sess.snapshot(f"Move layer {index} to {to}")
    layer_mod.move_layer(sess.get_project(), index, to)
    output({"moved": index, "to": to}, f"Moved layer {index} to position {to}")


@layer.command(
    "set", context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
@click.pass_context
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value", required=False)
@handle_error
def layer_set(ctx, index, prop, value):
    """Set a layer property (name, opacity, visible, mode, offset_x, offset_y)."""
    if value is None:
        if not ctx.args:
            raise ValueError("Missing layer property value")
        value = ctx.args[0]
    elif ctx.args:
        value = " ".join([value] + ctx.args)
    sess = get_session()
    sess.snapshot(f"Set layer {index} {prop}={value}")
    layer_mod.set_layer_property(sess.get_project(), index, prop, value)
    output(
        {"layer": index, "property": prop, "value": value},
        f"Set layer {index} {prop} = {value}",
    )
