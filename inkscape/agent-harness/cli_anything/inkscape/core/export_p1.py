# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _parse_color(color_str: str) -> Optional[str]:
    """Parse a CSS color string to a Pillow-compatible color string."""
    if not color_str or color_str.lower() in ("none", "transparent"):
        return None
    return color_str


def _get_style_val(obj: Dict[str, Any], key: str, default: str = "") -> str:
    """Get a style value from an object's style string."""
    from cli_anything.inkscape.utils.svg_utils import parse_style

    style = parse_style(obj.get("style", ""))
    return style.get(key, default)


def _parse_svg_points(points_str: str, sx: float = 1, sy: float = 1) -> list:
    """Parse SVG points string to list of (x, y) tuples."""
    import re

    result = []
    for pair in points_str.strip().split():
        parts = pair.split(",")
        if len(parts) == 2:
            try:
                result.append((float(parts[0]) * sx, float(parts[1]) * sy))
            except ValueError:
                pass
    return result


def _render_path_as_polygon(
    draw, d: str, fill, stroke, stroke_w: int, sx: float, sy: float
) -> None:
    """Render a simple SVG path as a Pillow polygon (handles M, L, Z only)."""
    import re

    points = []
    parts = re.split(r"[MLZmlz]", d)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        coords = re.split(r"[,\s]+", part)
        i = 0
        while i + 1 < len(coords):
            try:
                x = float(coords[i]) * sx
                y = float(coords[i + 1]) * sy
                points.append((x, y))
                i += 2
            except ValueError:
                i += 1

    if len(points) >= 3:
        draw.polygon(points, fill=fill, outline=stroke, width=stroke_w)
    elif len(points) == 2:
        line_color = stroke or fill or "#000000"
        draw.line([points[0], points[1]], fill=line_color, width=stroke_w)


def _resolve_text_line_x(
    draw, line: str, anchor_x: float, obj: Dict[str, Any], font, sx: float
) -> float:
    """Resolve actual line x-position for Pillow drawing."""
    anchor = obj.get("text_anchor", "start")
    if anchor == "start":
        return anchor_x

    try:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
    except Exception:
        width = len(line) * max(1.0, float(obj.get("font_size", 24)) * 0.58 * sx)

    if anchor == "middle":
        return anchor_x - (width / 2.0)
    if anchor == "end":
        return anchor_x - width
    return anchor_x
