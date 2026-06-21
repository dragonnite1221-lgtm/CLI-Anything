# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _load_font  # noqa: E402,E501
# fmt: on


def _apply_draw_ops(img, draw_ops):
    """Apply stored draw operations onto a layer image."""
    if not draw_ops:
        return img

    from PIL import ImageDraw, ImageFont

    canvas = img.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    for op in draw_ops:
        op_type = op.get("type")
        if op_type == "rect":
            fill = op.get("fill")
            outline = op.get("outline")
            line_width = max(1, int(op.get("width", 1)))
            draw.rectangle(
                [op.get("x1", 0), op.get("y1", 0), op.get("x2", 0), op.get("y2", 0)],
                fill=fill,
                outline=outline,
                width=line_width,
            )
        elif op_type == "text":
            font_size = int(op.get("size", 24))
            font_name = op.get("font", "Arial")
            font = _load_font(font_name, font_size)
            draw.text(
                (op.get("x", 0), op.get("y", 0)),
                op.get("text", ""),
                fill=op.get("color", "#000000"),
                font=font,
            )

    return canvas


def _apply_sepia(img, strength=0.8):
    """Apply sepia tone effect (Pillow fallback path)."""
    from PIL import Image as PILImage, ImageOps

    needs_rgba = img.mode == "RGBA"
    if needs_rgba:
        alpha = img.split()[3]

    gray = ImageOps.grayscale(img)
    sepia = ImageOps.colorize(gray, "#704214", "#C0A080")

    if strength < 1.0:
        rgb = img.convert("RGB")
        sepia = PILImage.blend(rgb, sepia, strength)

    if needs_rgba:
        sepia = sepia.convert("RGBA")
        sepia.putalpha(alpha)

    return sepia
