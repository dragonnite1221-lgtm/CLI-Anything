# ruff: noqa: F403, F405, E501
from .paths_base import *  # noqa: F403


def _shape_to_path_data(obj: Dict[str, Any]) -> Optional[str]:
    """Convert a basic shape to SVG path data.

    Returns None if conversion requires Inkscape.
    """
    obj_type = obj.get("type", "")

    if obj_type == "rect":
        x = float(obj.get("x", 0))
        y = float(obj.get("y", 0))
        w = float(obj.get("width", 100))
        h = float(obj.get("height", 100))
        rx = float(obj.get("rx", 0))
        ry = float(obj.get("ry", 0))

        if rx == 0 and ry == 0:
            return f"M {x},{y} L {x + w},{y} L {x + w},{y + h} L {x},{y + h} Z"
        else:
            # Rounded rectangle
            rx = min(rx, w / 2)
            ry = min(ry, h / 2)
            return (
                f"M {x + rx},{y} "
                f"L {x + w - rx},{y} "
                f"A {rx},{ry} 0 0 1 {x + w},{y + ry} "
                f"L {x + w},{y + h - ry} "
                f"A {rx},{ry} 0 0 1 {x + w - rx},{y + h} "
                f"L {x + rx},{y + h} "
                f"A {rx},{ry} 0 0 1 {x},{y + h - ry} "
                f"L {x},{y + ry} "
                f"A {rx},{ry} 0 0 1 {x + rx},{y} Z"
            )

    elif obj_type == "circle":
        cx = float(obj.get("cx", 50))
        cy = float(obj.get("cy", 50))
        r = float(obj.get("r", 50))
        # Circle as two arcs
        return (
            f"M {cx - r},{cy} "
            f"A {r},{r} 0 1 0 {cx + r},{cy} "
            f"A {r},{r} 0 1 0 {cx - r},{cy} Z"
        )

    elif obj_type == "ellipse":
        cx = float(obj.get("cx", 50))
        cy = float(obj.get("cy", 50))
        rx = float(obj.get("rx", 75))
        ry = float(obj.get("ry", 50))
        return (
            f"M {cx - rx},{cy} "
            f"A {rx},{ry} 0 1 0 {cx + rx},{cy} "
            f"A {rx},{ry} 0 1 0 {cx - rx},{cy} Z"
        )

    elif obj_type == "line":
        x1 = float(obj.get("x1", 0))
        y1 = float(obj.get("y1", 0))
        x2 = float(obj.get("x2", 100))
        y2 = float(obj.get("y2", 100))
        return f"M {x1},{y1} L {x2},{y2}"

    elif obj_type == "polygon":
        points_str = obj.get("points", "")
        if not points_str:
            return None
        return "M " + " L ".join(points_str.strip().split()) + " Z"

    elif obj_type == "polyline":
        points_str = obj.get("points", "")
        if not points_str:
            return None
        return "M " + " L ".join(points_str.strip().split())

    return None


def convert_to_path(
    project: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Convert a shape to a path element.

    For basic shapes (rect, circle, ellipse), we can compute the
    equivalent SVG path data. For complex shapes, we record the
    conversion as a pending operation for Inkscape.
    """
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    obj = objects[index]
    obj_type = obj.get("type", "")

    if obj_type == "path":
        return obj  # Already a path

    if obj_type not in CONVERTIBLE_TYPES:
        raise ValueError(
            f"Cannot convert type '{obj_type}' to path. "
            f"Convertible types: {', '.join(sorted(CONVERTIBLE_TYPES))}"
        )

    # Convert basic shapes to path data
    d = _shape_to_path_data(obj)

    if d is not None:
        obj["type"] = "path"
        obj["d"] = d
        obj["original_type"] = obj_type
    else:
        # For complex conversions, mark as pending
        obj["type"] = "path"
        obj["d"] = obj.get("d", "M 0,0")
        obj["original_type"] = obj_type
        obj["conversion_pending"] = True

    return obj


def list_path_operations() -> List[Dict[str, str]]:
    """List available path boolean operations."""
    return [
        {
            "name": name,
            "description": spec["description"],
            "inkscape_action": spec["inkscape_action"],
        }
        for name, spec in PATH_OPERATIONS.items()
    ]
