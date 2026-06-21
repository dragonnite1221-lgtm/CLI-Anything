# ruff: noqa: F403, F405, E501
from .text_base import *  # noqa: F403

# fmt: off
from .text_p2 import _wrap_paragraph  # noqa: E402,E501
# fmt: on


def _truncate_with_ellipsis(text: str, max_chars: int) -> str:
    """Trim text to fit and add an ellipsis when needed."""
    if len(text) <= max_chars:
        return text
    if max_chars <= 1:
        return text[:max_chars]
    return text[: max_chars - 1].rstrip() + "…"


def layout_text_lines(obj: Dict[str, Any]) -> List[str]:
    """Lay out wrapped text lines for a text object."""
    text = str(obj.get("text", ""))
    if not text:
        return [""]

    box_width = obj.get("box_width")
    line_height = float(obj.get("line_height", 1.2) or 1.2)
    font_size = float(obj.get("font_size", 24) or 24)

    if not box_width:
        return text.splitlines() or [text]

    avg_char_width = max(1.0, font_size * 0.58)
    max_chars = max(1, int(float(box_width) / avg_char_width))

    lines: List[str] = []
    for paragraph in text.splitlines() or [text]:
        wrapped = _wrap_paragraph(paragraph, max_chars)
        lines.extend(wrapped or [""])

    box_height = obj.get("box_height")
    if box_height:
        max_lines = max(1, int(float(box_height) / max(1.0, font_size * line_height)))
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = _truncate_with_ellipsis(lines[-1], max_chars)

    return lines


def text_anchor_x(obj: Dict[str, Any]) -> float:
    """Compute the anchor x-position, taking text boxes into account."""
    x = float(obj.get("x", 0))
    box_width = obj.get("box_width")
    anchor = obj.get("text_anchor", "start")
    if not box_width:
        return x
    if anchor == "middle":
        return x + float(box_width) / 2.0
    if anchor == "end":
        return x + float(box_width)
    return x
