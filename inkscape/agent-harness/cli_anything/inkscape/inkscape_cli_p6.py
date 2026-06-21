# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli  # noqa: E402,E501
# fmt: on


@cli.group()
def layer():
    """Layer management commands."""
    pass


@layer.command("add")
@click.option("--name", "-n", default="New Layer", help="Layer name")
@click.option("--visible/--hidden", default=True)
@click.option("--opacity", type=float, default=1.0)
@click.option("--position", type=int, default=None, help="Stack position")
@handle_error
def layer_add(name, visible, opacity, position):
    """Add a new layer."""
    sess = get_session()
    sess.snapshot(f"Add layer: {name}")
    layer = layer_mod.add_layer(
        sess.get_project(),
        name=name,
        visible=visible,
        opacity=opacity,
        position=position,
    )
    output(layer, f"Added layer: {layer['name']}")


@layer.command("remove")
@click.argument("index", type=int)
@handle_error
def layer_remove(index):
    """Remove a layer by index."""
    sess = get_session()
    sess.snapshot(f"Remove layer {index}")
    removed = layer_mod.remove_layer(sess.get_project(), index)
    output(removed, f"Removed layer: {removed.get('name', '')}")


@layer.command("move-object")
@click.argument("object_index", type=int)
@click.argument("layer_index", type=int)
@handle_error
def layer_move_object(object_index, layer_index):
    """Move an object to a different layer."""
    sess = get_session()
    sess.snapshot(f"Move object {object_index} to layer {layer_index}")
    result = layer_mod.move_to_layer(sess.get_project(), object_index, layer_index)
    output(result, f"Moved {result['object']} to {result['target_layer']}")


@layer.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def layer_set(index, prop, value):
    """Set a layer property (name, visible, locked, opacity)."""
    sess = get_session()
    sess.snapshot(f"Set layer {index} {prop}")
    layer_mod.set_layer_property(sess.get_project(), index, prop, value)
    output(
        {"layer": index, "property": prop, "value": value},
        f"Set layer {index} {prop} = {value}",
    )


@layer.command("list")
@handle_error
def layer_list():
    """List all layers."""
    sess = get_session()
    layers = layer_mod.list_layers(sess.get_project())
    output(layers, "Layers:")


@layer.command("reorder")
@click.argument("from_index", type=int)
@click.argument("to_index", type=int)
@handle_error
def layer_reorder(from_index, to_index):
    """Move a layer from one position to another."""
    sess = get_session()
    sess.snapshot(f"Reorder layer {from_index} to {to_index}")
    result = layer_mod.reorder_layers(sess.get_project(), from_index, to_index)
    output(result, f"Moved layer: {result['layer']}")


@layer.command("get")
@click.argument("index", type=int)
@handle_error
def layer_get(index):
    """Get detailed info about a layer."""
    sess = get_session()
    layer = layer_mod.get_layer(sess.get_project(), index)
    output(layer)


@cli.group("path")
def path_group():
    """Path boolean operations."""
    pass


@path_group.command("union")
@click.argument("index_a", type=int)
@click.argument("index_b", type=int)
@click.option("--name", "-n", default=None)
@handle_error
def path_union(index_a, index_b, name):
    """Union of two objects."""
    sess = get_session()
    sess.snapshot(f"Path union {index_a} + {index_b}")
    result = path_mod.path_union(sess.get_project(), index_a, index_b, name)
    output(result, f"Union created: {result['name']}")


@path_group.command("intersection")
@click.argument("index_a", type=int)
@click.argument("index_b", type=int)
@click.option("--name", "-n", default=None)
@handle_error
def path_intersection(index_a, index_b, name):
    """Intersection of two objects."""
    sess = get_session()
    sess.snapshot(f"Path intersection {index_a} & {index_b}")
    result = path_mod.path_intersection(sess.get_project(), index_a, index_b, name)
    output(result, f"Intersection created: {result['name']}")


@path_group.command("difference")
@click.argument("index_a", type=int)
@click.argument("index_b", type=int)
@click.option("--name", "-n", default=None)
@handle_error
def path_difference(index_a, index_b, name):
    """Difference of two objects (A minus B)."""
    sess = get_session()
    sess.snapshot(f"Path difference {index_a} - {index_b}")
    result = path_mod.path_difference(sess.get_project(), index_a, index_b, name)
    output(result, f"Difference created: {result['name']}")


@path_group.command("exclusion")
@click.argument("index_a", type=int)
@click.argument("index_b", type=int)
@click.option("--name", "-n", default=None)
@handle_error
def path_exclusion(index_a, index_b, name):
    """Exclusion (XOR) of two objects."""
    sess = get_session()
    sess.snapshot(f"Path exclusion {index_a} ^ {index_b}")
    result = path_mod.path_exclusion(sess.get_project(), index_a, index_b, name)
    output(result, f"Exclusion created: {result['name']}")


@path_group.command("convert")
@click.argument("index", type=int)
@handle_error
def path_convert(index):
    """Convert a shape to a path."""
    sess = get_session()
    sess.snapshot(f"Convert object {index} to path")
    result = path_mod.convert_to_path(sess.get_project(), index)
    output(result, f"Converted to path: {result['name']}")
