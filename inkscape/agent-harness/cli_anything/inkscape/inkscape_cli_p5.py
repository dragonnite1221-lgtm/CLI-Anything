# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli  # noqa: E402,E501
from .inkscape_cli_p3 import style  # noqa: E402,E501
# fmt: on


@style.command("set-stroke")
@click.argument("index", type=int)
@click.argument("color")
@click.option("--width", "-w", type=float, default=None, help="Stroke width")
@handle_error
def style_set_stroke(index, color, width):
    """Set the stroke color (and optionally width) of an object."""
    sess = get_session()
    sess.snapshot(f"Set stroke on object {index}")
    style_mod.set_stroke(sess.get_project(), index, color, width)
    output({"object": index, "stroke": color, "width": width}, f"Set stroke: {color}")


@style.command("set-opacity")
@click.argument("index", type=int)
@click.argument("opacity", type=float)
@handle_error
def style_set_opacity(index, opacity):
    """Set the opacity of an object (0.0-1.0)."""
    sess = get_session()
    sess.snapshot(f"Set opacity on object {index}")
    style_mod.set_opacity(sess.get_project(), index, opacity)
    output({"object": index, "opacity": opacity}, f"Set opacity: {opacity}")


@style.command("set")
@click.argument("index", type=int)
@click.argument("prop")
@click.argument("value")
@handle_error
def style_set(index, prop, value):
    """Set an arbitrary style property on an object."""
    sess = get_session()
    sess.snapshot(f"Set style {prop} on object {index}")
    style_mod.set_style(sess.get_project(), index, prop, value)
    output({"object": index, "property": prop, "value": value}, f"Set {prop}: {value}")


@style.command("get")
@click.argument("index", type=int)
@handle_error
def style_get(index):
    """Get the style properties of an object."""
    sess = get_session()
    props = style_mod.get_object_style(sess.get_project(), index)
    output(props)


@style.command("list-properties")
@handle_error
def style_list_properties():
    """List all available style properties."""
    props = style_mod.list_style_properties()
    output(props, "Available style properties:")


@cli.group()
def transform():
    """Transform operations (translate, rotate, scale, skew)."""
    pass


@transform.command("translate")
@click.argument("index", type=int)
@click.argument("tx", type=float)
@click.option("--ty", type=float, default=0, help="Y translation")
@handle_error
def transform_translate(index, tx, ty):
    """Translate (move) an object."""
    sess = get_session()
    sess.snapshot(f"Translate object {index}")
    xform_mod.translate(sess.get_project(), index, tx, ty)
    output(
        {"object": index, "translate": f"{tx},{ty}"},
        f"Translated object {index} by ({tx}, {ty})",
    )


@transform.command("rotate")
@click.argument("index", type=int)
@click.argument("angle", type=float)
@click.option("--cx", type=float, default=None, help="Center X")
@click.option("--cy", type=float, default=None, help="Center Y")
@handle_error
def transform_rotate(index, angle, cx, cy):
    """Rotate an object."""
    sess = get_session()
    sess.snapshot(f"Rotate object {index}")
    xform_mod.rotate(sess.get_project(), index, angle, cx, cy)
    output(
        {"object": index, "rotate": angle}, f"Rotated object {index} by {angle} degrees"
    )


@transform.command("scale")
@click.argument("index", type=int)
@click.argument("sx", type=float)
@click.option("--sy", type=float, default=None, help="Y scale (default=sx)")
@handle_error
def transform_scale(index, sx, sy):
    """Scale an object."""
    sess = get_session()
    sess.snapshot(f"Scale object {index}")
    xform_mod.scale(sess.get_project(), index, sx, sy)
    output(
        {"object": index, "scale": f"{sx},{sy or sx}"},
        f"Scaled object {index} by ({sx}, {sy or sx})",
    )


@transform.command("skew-x")
@click.argument("index", type=int)
@click.argument("angle", type=float)
@handle_error
def transform_skew_x(index, angle):
    """Skew an object horizontally."""
    sess = get_session()
    sess.snapshot(f"Skew X object {index}")
    xform_mod.skew_x(sess.get_project(), index, angle)
    output(
        {"object": index, "skewX": angle},
        f"Skewed object {index} horizontally by {angle} degrees",
    )


@transform.command("skew-y")
@click.argument("index", type=int)
@click.argument("angle", type=float)
@handle_error
def transform_skew_y(index, angle):
    """Skew an object vertically."""
    sess = get_session()
    sess.snapshot(f"Skew Y object {index}")
    xform_mod.skew_y(sess.get_project(), index, angle)
    output(
        {"object": index, "skewY": angle},
        f"Skewed object {index} vertically by {angle} degrees",
    )


@transform.command("get")
@click.argument("index", type=int)
@handle_error
def transform_get(index):
    """Get the current transform of an object."""
    sess = get_session()
    t = xform_mod.get_transform(sess.get_project(), index)
    output(t)


@transform.command("clear")
@click.argument("index", type=int)
@handle_error
def transform_clear(index):
    """Clear all transforms from an object."""
    sess = get_session()
    sess.snapshot(f"Clear transform on object {index}")
    result = xform_mod.clear_transform(sess.get_project(), index)
    output(result, f"Cleared transforms on object {index}")
