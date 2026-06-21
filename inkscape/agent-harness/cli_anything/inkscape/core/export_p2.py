# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _get_style_val, _parse_color, _parse_svg_points, _render_path_as_polygon, _resolve_text_line_x  # noqa: E402,E501
# fmt: on


def _render_object(draw, obj: Dict[str, Any], sx: float, sy: float) -> None:
    """Render a single object onto a Pillow ImageDraw canvas."""
    obj_type = obj.get("type", "")
    fill = _parse_color(_get_style_val(obj, "fill", "#0000ff"))
    stroke = _parse_color(_get_style_val(obj, "stroke", "none"))
    stroke_w = _get_style_val(obj, "stroke-width", "1")
    try:
        stroke_w = max(1, int(float(stroke_w)))
    except (ValueError, TypeError):
        stroke_w = 1

    if obj_type == "rect":
        x = float(obj.get("x", 0)) * sx
        y = float(obj.get("y", 0)) * sy
        w = float(obj.get("width", 100)) * sx
        h = float(obj.get("height", 100)) * sy
        draw.rectangle([x, y, x + w, y + h], fill=fill, outline=stroke, width=stroke_w)

    elif obj_type == "circle":
        cx = float(obj.get("cx", 50)) * sx
        cy = float(obj.get("cy", 50)) * sy
        r = float(obj.get("r", 50)) * sx
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r], fill=fill, outline=stroke, width=stroke_w
        )

    elif obj_type == "ellipse":
        cx = float(obj.get("cx", 50)) * sx
        cy = float(obj.get("cy", 50)) * sy
        rx = float(obj.get("rx", 75)) * sx
        ry = float(obj.get("ry", 50)) * sy
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=fill,
            outline=stroke,
            width=stroke_w,
        )

    elif obj_type == "line":
        x1 = float(obj.get("x1", 0)) * sx
        y1 = float(obj.get("y1", 0)) * sy
        x2 = float(obj.get("x2", 100)) * sx
        y2 = float(obj.get("y2", 100)) * sy
        line_color = stroke or fill or "#000000"
        draw.line([x1, y1, x2, y2], fill=line_color, width=stroke_w)

    elif obj_type == "polygon":
        points_str = obj.get("points", "")
        if points_str:
            points = _parse_svg_points(points_str, sx, sy)
            if len(points) >= 2:
                draw.polygon(points, fill=fill, outline=stroke, width=stroke_w)

    elif obj_type == "text":
        anchor_x = text_anchor_x(obj) * sx
        y = float(obj.get("y", 50)) * sy
        text_fill = fill or "#000000"
        font_size = int(float(obj.get("font_size", 24)) * sy)
        line_height = float(obj.get("line_height", 1.2) or 1.2)
        try:
            from PIL import ImageFont

            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
            )
        except (ImportError, OSError):
            font = None
        for idx, line in enumerate(layout_text_lines(obj)):
            x = _resolve_text_line_x(draw, line, anchor_x, obj, font, sx)
            line_y = y + (idx * font_size * line_height)
            draw.text((x, line_y), line, fill=text_fill, font=font)

    elif obj_type == "star" and "d" in obj:
        # Render star as polygon from path data
        _render_path_as_polygon(draw, obj.get("d", ""), fill, stroke, stroke_w, sx, sy)

    elif obj_type == "path":
        # Basic path rendering
        _render_path_as_polygon(draw, obj.get("d", ""), fill, stroke, stroke_w, sx, sy)
