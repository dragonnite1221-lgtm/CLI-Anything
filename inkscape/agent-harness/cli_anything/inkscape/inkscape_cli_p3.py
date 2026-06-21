# ruff: noqa: F403, F405, E501
from .inkscape_cli_base import *  # noqa: F403

# fmt: off
from .inkscape_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .inkscape_cli_p2 import cli, document  # noqa: E402,E501
# fmt: on


@document.command("save")
@click.argument("path", required=False)
@handle_error
def document_save(path):
    """Save the current project."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@document.command("info")
@handle_error
def document_info():
    """Show document information."""
    sess = get_session()
    info = doc_mod.get_document_info(sess.get_project())
    output(info)


@document.command("profiles")
@handle_error
def document_profiles():
    """List available document profiles."""
    profiles = doc_mod.list_profiles()
    output(profiles, "Available profiles:")


@document.command("canvas-size")
@click.option("--width", "-w", type=float, required=True)
@click.option("--height", "-h", type=float, required=True)
@handle_error
def document_canvas_size(width, height):
    """Set the canvas size."""
    sess = get_session()
    sess.snapshot("Set canvas size")
    result = doc_mod.set_canvas_size(sess.get_project(), width, height)
    output(result, f"Canvas resized: {result['new_size']}")


@document.command("units")
@click.argument("units", type=click.Choice(["px", "mm", "cm", "in", "pt", "pc"]))
@handle_error
def document_units(units):
    """Set the document units."""
    sess = get_session()
    result = doc_mod.set_units(sess.get_project(), units)
    output(result, f"Units changed: {result['old_units']} -> {result['new_units']}")


@document.command("json")
@handle_error
def document_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group()
def shape():
    """Shape management commands."""
    pass


@cli.group()
def style():
    """Style management commands."""
    pass


@shape.command("add-rect")
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--width", "-w", type=float, default=100)
@click.option("--height", "-h", type=float, default=100)
@click.option("--rx", type=float, default=0, help="Corner radius X")
@click.option("--ry", type=float, default=0, help="Corner radius Y")
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None, help="CSS style string")
@handle_error
def shape_add_rect(x, y, width, height, rx, ry, name, style):
    """Add a rectangle."""
    sess = get_session()
    sess.snapshot("Add rectangle")
    obj = shape_mod.add_rect(
        sess.get_project(),
        x=x,
        y=y,
        width=width,
        height=height,
        rx=rx,
        ry=ry,
        name=name,
        style=style,
    )
    output(obj, f"Added rectangle: {obj['name']}")


@shape.command("add-circle")
@click.option("--cx", type=float, default=50)
@click.option("--cy", type=float, default=50)
@click.option("--r", type=float, default=50, help="Radius")
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_circle(cx, cy, r, name, style):
    """Add a circle."""
    sess = get_session()
    sess.snapshot("Add circle")
    obj = shape_mod.add_circle(
        sess.get_project(), cx=cx, cy=cy, r=r, name=name, style=style
    )
    output(obj, f"Added circle: {obj['name']}")


@shape.command("add-ellipse")
@click.option("--cx", type=float, default=50)
@click.option("--cy", type=float, default=50)
@click.option("--rx", type=float, default=75)
@click.option("--ry", type=float, default=50)
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_ellipse(cx, cy, rx, ry, name, style):
    """Add an ellipse."""
    sess = get_session()
    sess.snapshot("Add ellipse")
    obj = shape_mod.add_ellipse(
        sess.get_project(), cx=cx, cy=cy, rx=rx, ry=ry, name=name, style=style
    )
    output(obj, f"Added ellipse: {obj['name']}")


@shape.command("add-line")
@click.option("--x1", type=float, default=0)
@click.option("--y1", type=float, default=0)
@click.option("--x2", type=float, default=100)
@click.option("--y2", type=float, default=100)
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_line(x1, y1, x2, y2, name, style):
    """Add a line."""
    sess = get_session()
    sess.snapshot("Add line")
    obj = shape_mod.add_line(
        sess.get_project(), x1=x1, y1=y1, x2=x2, y2=y2, name=name, style=style
    )
    output(obj, f"Added line: {obj['name']}")


@shape.command("add-polygon")
@click.option(
    "--points", "-p", required=True, help='SVG points, e.g. "50,0 100,100 0,100"'
)
@click.option("--name", "-n", default=None)
@click.option("--style", "-s", default=None)
@handle_error
def shape_add_polygon(points, name, style):
    """Add a polygon."""
    sess = get_session()
    sess.snapshot("Add polygon")
    obj = shape_mod.add_polygon(
        sess.get_project(), points=points, name=name, style=style
    )
    output(obj, f"Added polygon: {obj['name']}")
