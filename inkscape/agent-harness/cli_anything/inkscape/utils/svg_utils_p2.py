# ruff: noqa: F403, F405, E501
from .svg_utils_base import *  # noqa: F403


def remove_element_by_id(svg: ET.Element, element_id: str) -> bool:
    """Remove an element by id. Returns True if found and removed."""
    for parent in svg.iter():
        for child in list(parent):
            if child.get("id") == element_id:
                parent.remove(child)
                return True
    return False


def validate_color(color: str) -> bool:
    """Validate a CSS color string (hex, named, rgb, none)."""
    if not color:
        return False
    color = color.strip().lower()
    if color in ("none", "transparent", "currentcolor", "inherit"):
        return True
    # Hex colors
    if re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", color):
        return True
    # rgb()/rgba()
    if re.match(r"^rgba?\(", color):
        return True
    # Named CSS colors (just check it's alpha chars)
    if re.match(r"^[a-z]+$", color):
        return True
    return False
