# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_constraint_id, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_polygon_sketch(
    project: Dict[str, Any],
    sketch_index: int,
    center: Optional[List[float]] = None,
    sides: int = 6,
    radius: float = 5.0,
) -> Dict[str, Any]:
    """Add a regular polygon to a sketch (N lines + N coincident constraints).

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    center:
        Center point ``[x, y]``.  Defaults to ``[0, 0]``.
    sides:
        Number of sides.  Must be at least 3.
    radius:
        Circumscribed circle radius.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        Summary containing line element IDs and coincident constraint IDs.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    center = _validate_point_2d(center if center is not None else [0, 0], "center")
    sides = int(sides)
    radius = float(radius)

    if sides < 3:
        raise ValueError(f"Polygon must have at least 3 sides, got {sides}")
    if radius <= 0:
        raise ValueError(f"Radius must be positive, got {radius}")

    cx, cy = center

    # Compute vertices
    vertices: List[List[float]] = []
    for i in range(sides):
        angle_rad = 2 * math.pi * i / sides
        vertices.append(
            [
                cx + radius * math.cos(angle_rad),
                cy + radius * math.sin(angle_rad),
            ]
        )

    # Create line elements for each side
    lines: List[Dict[str, Any]] = []
    for i in range(sides):
        j = (i + 1) % sides
        elem: Dict[str, Any] = {
            "id": _next_element_id(sketch),
            "type": "line",
            "start": list(vertices[i]),
            "end": list(vertices[j]),
        }
        sketch["elements"].append(elem)
        lines.append(elem)

    # Add coincident constraints at each vertex (adjacent lines)
    constraint_ids: List[int] = []
    for i in range(sides):
        j = (i + 1) % sides
        constraint: Dict[str, Any] = {
            "id": _next_constraint_id(sketch),
            "type": "coincident",
            "elements": [lines[i]["id"], lines[j]["id"]],
            "value": None,
        }
        sketch["constraints"].append(constraint)
        constraint_ids.append(constraint["id"])

    return {
        "type": "polygon",
        "line_ids": [line["id"] for line in lines],
        "constraint_ids": constraint_ids,
        "center": center,
        "sides": sides,
        "radius": radius,
    }
