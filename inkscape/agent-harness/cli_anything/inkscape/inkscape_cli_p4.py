# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli  # noqa: E402,E501
from .inkscape_cli_p3 import shape, style  # noqa: E402,E501
# fmt: on


@shape.command("add-path")
@click.option(
    "--d", required=True, help='SVG path data, e.g. "M 0,0 L 100,0 L 100,100 Z"'
)
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_path(d, name, style):
    """Add a path."""
    sess = get_session()
    sess.snapshot("Add path")
    obj = shape_mod.add_path(sess.get_project(), d=d, name=name, style=style)
    output(obj, f"Added path: {obj['name']}")


@shape.command("add-star")
@click.option("--cx", type=float, default=50)
@click.option("--cy", type=float, default=50)
@click.option("--points", type=int, default=5, help="Number of star points")
@click.option("--outer-r", type=float, default=50, help="Outer radius")
@click.option("--inner-r", type=float, default=25, help="Inner radius")
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_star(cx, cy, points, outer_r, inner_r, name, style):
    """Add a star."""
    sess = get_session()
    sess.snapshot("Add star")
    obj = shape_mod.add_star(
        sess.get_project(),
        cx=cx,
        cy=cy,
        points_count=points,
        outer_r=outer_r,
        inner_r=inner_r,
        name=name,
        style=style,
    )
    output(obj, f"Added star: {obj['name']}")


@shape.command("remove")
@click.argument("index", type=int)
@handle_error
def shape_remove(index):
    """Remove a shape by index."""
    sess = get_session()
    sess.snapshot(f"Remove object {index}")
    removed = shape_mod.remove_object(sess.get_project(), index)
    output(removed, f"Removed: {removed.get('name', '')}")


@shape.command("duplicate")
@click.argument("index", type=int)
@handle_error
def shape_duplicate(index):
    """Duplicate a shape."""
    sess = get_session()
    sess.snapshot(f"Duplicate object {index}")
    dup = shape_mod.duplicate_object(sess.get_project(), index)
    output(dup, f"Duplicated: {dup['name']}")


@shape.command("list")
@handle_error
def shape_list():
    """List all shapes/objects."""
    sess = get_session()
    objects = shape_mod.list_objects(sess.get_project())
    output(objects, "Objects:")


@shape.command("get")
@click.argument("index", type=int)
@handle_error
def shape_get(index):
    """Get detailed info about a shape."""
    sess = get_session()
    obj = shape_mod.get_object(sess.get_project(), index)
    output(obj)


@cli.group()
def text():
    """Text management commands."""
    pass


@text.command("add")
@click.option("--text", "-t", required=True, help="Text content")
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=50)
@click.option("--font-family", default="sans-serif", help="Font family")
@click.option("--font-size", type=float, default=24, help="Font size in px")
@click.option("--font-weight", default="normal", help="Font weight")
@click.option("--fill", default="#000000", help="Text color")
@click.option("--text-anchor", default="start", help="Alignment: start, middle, end")
@click.option(
    "--box-width", type=float, default=None, help="Optional text box width for wrapping"
)
@click.option(
    "--box-height",
    type=float,
    default=None,
    help="Optional text box height for wrapping",
)
@click.option("--line-height", type=float, default=1.2, help="Line height multiplier")
@click.option("--name", "-n", default=None)
@handle_error
def text_add(
    text,
    x,
    y,
    font_family,
    font_size,
    font_weight,
    fill,
    text_anchor,
    box_width,
    box_height,
    line_height,
    name,
):
    """Add a text element."""
    sess = get_session()
    sess.snapshot("Add text")
    obj = text_mod.add_text(
        sess.get_project(),
        text=text,
        x=x,
        y=y,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        fill=fill,
        text_anchor=text_anchor,
        box_width=box_width,
        box_height=box_height,
        line_height=line_height,
        name=name,
    )
    output(obj, f"Added text: {obj['name']}")


@text.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def text_set(index, prop, value):
    """Set a text property (text, font-family, font-size, fill, etc.)."""
    sess = get_session()
    sess.snapshot(f"Set text {index} {prop}")
    text_mod.set_text_property(sess.get_project(), index, prop, value)
    output(
        {"object": index, "property": prop, "value": value},
        f"Set text {index} {prop} = {value}",
    )


@text.command("list")
@handle_error
def text_list():
    """List all text objects."""
    sess = get_session()
    texts = text_mod.list_text_objects(sess.get_project())
    output(texts, "Text objects:")


@style.command("set-fill")
@click.argument("index", type=int)
@click.argument("color")
@handle_error
def style_set_fill(index, color):
    """Set the fill color of an object."""
    sess = get_session()
    sess.snapshot(f"Set fill on object {index}")
    style_mod.set_fill(sess.get_project(), index, color)
    output({"object": index, "fill": color}, f"Set fill: {color}")
