# ruff: noqa: F403, F405, E501
from .text_base import *  # noqa: F403

# fmt: off
from .text_p1 import _rebuild_text_style  # noqa: E402,E501
# fmt: on


def set_text_property(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> Dict[str, Any]:
    """Set a property on a text object.

    Args:
        index: Object index in the objects list.
        prop: Property name (from TEXT_PROPERTIES).
        value: New value.

    Returns:
        Updated object dict.
    """
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    obj = objects[index]
    if obj.get("type") != "text":
        raise ValueError(
            f"Object at index {index} is not a text element (type={obj.get('type')})"
        )

    if prop not in TEXT_PROPERTIES:
        raise ValueError(
            f"Unknown text property: {prop}. Valid: {', '.join(TEXT_PROPERTIES.keys())}"
        )

    # Validate specific properties
    if prop == "font-weight" and str(value) not in VALID_FONT_WEIGHTS:
        raise ValueError(
            f"Invalid font-weight: {value}. Valid: {', '.join(VALID_FONT_WEIGHTS)}"
        )
    if prop == "font-style" and str(value) not in VALID_FONT_STYLES:
        raise ValueError(
            f"Invalid font-style: {value}. Valid: {', '.join(VALID_FONT_STYLES)}"
        )
    if prop == "text-anchor" and str(value) not in VALID_TEXT_ANCHORS:
        raise ValueError(
            f"Invalid text-anchor: {value}. Valid: {', '.join(VALID_TEXT_ANCHORS)}"
        )
    if prop == "text-decoration" and str(value) not in VALID_TEXT_DECORATIONS:
        raise ValueError(
            f"Invalid text-decoration: {value}. Valid: {', '.join(VALID_TEXT_DECORATIONS)}"
        )
    if prop == "font-size":
        value = float(value)
        if value <= 0:
            raise ValueError(f"Font size must be positive: {value}")
    if prop in {"box-width", "box-height"}:
        value = float(value)
        if value <= 0:
            raise ValueError(f"{prop} must be positive: {value}")
    if prop == "line-height":
        value = float(value)
        if value <= 0:
            raise ValueError(f"Line height must be positive: {value}")
    if prop == "opacity":
        value = float(value)
        if value < 0 or value > 1:
            raise ValueError(f"Opacity must be 0.0-1.0: {value}")

    # Apply the property
    # Map CSS property names to internal field names
    field_map = {
        "font-family": "font_family",
        "font-size": "font_size",
        "font-weight": "font_weight",
        "font-style": "font_style",
        "text-anchor": "text_anchor",
        "text-decoration": "text_decoration",
        "letter-spacing": "letter_spacing",
        "word-spacing": "word_spacing",
        "line-height": "line_height",
        "box-width": "box_width",
        "box-height": "box_height",
    }

    internal_name = field_map.get(prop, prop)
    obj[internal_name] = value

    # Rebuild style string
    _rebuild_text_style(obj)

    return obj


def list_text_objects(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all text objects in the document."""
    result = []
    for i, obj in enumerate(project.get("objects", [])):
        if obj.get("type") == "text":
            result.append(
                {
                    "index": i,
                    "id": obj.get("id", ""),
                    "name": obj.get("name", ""),
                    "text": obj.get("text", ""),
                    "font_family": obj.get("font_family", "sans-serif"),
                    "font_size": obj.get("font_size", 24),
                    "fill": obj.get("fill", "#000000"),
                    "x": obj.get("x", 0),
                    "y": obj.get("y", 0),
                    "box_width": obj.get("box_width"),
                    "box_height": obj.get("box_height"),
                }
            )
    return result


def _wrap_paragraph(paragraph: str, max_chars: int) -> List[str]:
    """Wrap a paragraph to an approximate character count."""
    words = paragraph.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            current = word
            continue

        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines
