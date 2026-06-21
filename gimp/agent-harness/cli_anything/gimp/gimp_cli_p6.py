# ruff: noqa: F403, F405, E501
from .gimp_cli_base import *  # noqa: F403

# fmt: off
from .gimp_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .gimp_cli_p5 import session  # noqa: E402,E501
# fmt: on


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


@cli.group()
def draw():
    """Drawing operations (applied at render time)."""
    pass


@draw.command("text")
@click.option("--layer", "-l", "layer_index", type=int, default=0)
@click.option("--text", "-t", required=True, help="Text to draw")
@click.option("--x", type=int, default=0, help="X position")
@click.option("--y", type=int, default=0, help="Y position")
@click.option("--font", default="Arial", help="Font name")
@click.option("--size", type=int, default=24, help="Font size")
@click.option("--color", default="#000000", help="Text color (hex)")
@handle_error
def draw_text(layer_index, text, x, y, font, size, color):
    """Draw text on a layer as a persisted draw operation."""
    sess = get_session()
    sess.snapshot(f"Draw text on layer {layer_index}")
    proj = sess.get_project()
    layers = proj.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(f"Layer index {layer_index} out of range")
    layer = layers[layer_index]
    layer.setdefault("draw_ops", []).append(
        {
            "type": "text",
            "text": text,
            "x": x,
            "y": y,
            "font": font,
            "size": size,
            "color": color,
        }
    )
    output({"layer": layer_index, "text": text}, f"Drew text on layer {layer_index}")


@draw.command("rect")
@click.option("--layer", "-l", "layer_index", type=int, default=0)
@click.option("--x1", type=int, required=True)
@click.option("--y1", type=int, required=True)
@click.option("--x2", type=int, required=True)
@click.option("--y2", type=int, required=True)
@click.option("--fill", default=None, help="Fill color (hex)")
@click.option("--outline", default=None, help="Outline color (hex)")
@click.option("--width", "line_width", type=int, default=1, help="Outline width")
@handle_error
def draw_rect(layer_index, x1, y1, x2, y2, fill, outline, line_width):
    """Draw a rectangle (stored as drawing operation)."""
    sess = get_session()
    sess.snapshot(f"Draw rect on layer {layer_index}")
    proj = sess.get_project()
    layers = proj.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(f"Layer index {layer_index} out of range")
    layer = layers[layer_index]
    if "draw_ops" not in layer:
        layer["draw_ops"] = []
    layer["draw_ops"].append(
        {
            "type": "rect",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "fill": fill,
            "outline": outline,
            "width": line_width,
        }
    )
    output(
        {"layer": layer_index, "shape": "rect", "coords": f"({x1},{y1})-({x2},{y2})"},
        f"Drew rectangle on layer {layer_index}",
    )


def main():
    cli()
