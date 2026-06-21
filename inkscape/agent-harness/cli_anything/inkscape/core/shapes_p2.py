# ruff: noqa: F403, F405, E501
from .shapes_base import *  # noqa: F403

# fmt: off
from .shapes_p1 import _add_object, _default_layer_id  # noqa: E402,E501
# fmt: on


def add_polygon(
    project: Dict[str, Any],
    points: str = "50,0 100,100 0,100",
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a polygon to the document.

    Args:
        points: SVG points string, e.g. "50,0 100,100 0,100"
    """
    if not points or not points.strip():
        raise ValueError("Polygon must have at least one point")

    obj_id = generate_id("polygon")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "polygon",
        "points": points,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def add_path(
    project: Dict[str, Any],
    d: str = "M 0,0 L 100,0 L 100,100 Z",
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a path to the document.

    Args:
        d: SVG path data string.
    """
    if not d or not d.strip():
        raise ValueError("Path data (d) cannot be empty")

    obj_id = generate_id("path")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "path",
        "d": d,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def _star_path(cx: float, cy: float, n: int, outer_r: float, inner_r: float) -> str:
    """Generate SVG path data for a star with n points."""
    points = []
    for i in range(2 * n):
        angle = math.pi * i / n - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append(f"{x:.2f},{y:.2f}")

    return "M " + " L ".join(points) + " Z"


def add_star(
    project: Dict[str, Any],
    cx: float = 50,
    cy: float = 50,
    points_count: int = 5,
    outer_r: float = 50,
    inner_r: float = 25,
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a star (regular polygon) to the document."""
    if points_count < 3:
        raise ValueError(f"Star must have at least 3 points: {points_count}")
    if outer_r <= 0 or inner_r <= 0:
        raise ValueError(
            f"Star radii must be positive: outer={outer_r}, inner={inner_r}"
        )

    # Generate star path data
    d = _star_path(cx, cy, points_count, outer_r, inner_r)

    obj_id = generate_id("star")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "star",
        "cx": cx,
        "cy": cy,
        "points_count": points_count,
        "outer_r": outer_r,
        "inner_r": inner_r,
        "d": d,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def remove_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove an object by index."""
    objects = project.get("objects", [])
    if not objects:
        raise ValueError("No objects in document")
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    removed = objects.pop(index)

    # Remove from layer
    obj_id = removed.get("id", "")
    for layer in project.get("layers", []):
        if obj_id in layer.get("objects", []):
            layer["objects"].remove(obj_id)

    return removed
