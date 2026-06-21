# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_slot(
    project: Dict[str, Any],
    sketch_index: int,
    center1: Optional[List[float]] = None,
    center2: Optional[List[float]] = None,
    radius: float = 2.0,
) -> Dict[str, Any]:
    """Add a slot (obround) shape to a sketch.

    The slot consists of two semicircular arcs connected by two lines.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    center1:
        Center of the first semicircle ``[x, y]``.  Defaults to ``[0, 0]``.
    center2:
        Center of the second semicircle ``[x, y]``.  Defaults to ``[10, 0]``.
    radius:
        Radius of the semicircular ends.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        Summary containing arc and line element IDs.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    center1 = _validate_point_2d(center1 if center1 is not None else [0, 0], "center1")
    center2 = _validate_point_2d(center2 if center2 is not None else [10, 0], "center2")
    radius = float(radius)

    if radius <= 0:
        raise ValueError(f"Radius must be positive, got {radius}")
    if center1 == center2:
        raise ValueError("center1 and center2 must be different")

    # Direction vector from center1 to center2
    dx = center2[0] - center1[0]
    dy = center2[1] - center1[1]
    length = math.sqrt(dx * dx + dy * dy)
    nx = -dy / length  # perpendicular normal
    ny = dx / length

    # Four connection points
    p1_top = [center1[0] + nx * radius, center1[1] + ny * radius]
    p1_bot = [center1[0] - nx * radius, center1[1] - ny * radius]
    p2_top = [center2[0] + nx * radius, center2[1] + ny * radius]
    p2_bot = [center2[0] - nx * radius, center2[1] - ny * radius]

    # Angle of the direction vector
    base_angle = math.degrees(math.atan2(dy, dx))

    # Arc at center1 (from bottom to top, going "left")
    arc1: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "arc",
        "center": list(center1),
        "radius": radius,
        "start_angle": base_angle + 90,
        "end_angle": base_angle + 270,
        "start_point": list(p1_top),
        "end_point": list(p1_bot),
    }
    sketch["elements"].append(arc1)

    # Top line from center1 to center2
    line_top: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "line",
        "start": list(p1_top),
        "end": list(p2_top),
    }
    sketch["elements"].append(line_top)

    # Arc at center2 (from top to bottom, going "right")
    arc2: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "arc",
        "center": list(center2),
        "radius": radius,
        "start_angle": base_angle - 90,
        "end_angle": base_angle + 90,
        "start_point": list(p2_bot),
        "end_point": list(p2_top),
    }
    sketch["elements"].append(arc2)

    # Bottom line from center2 to center1
    line_bot: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "line",
        "start": list(p2_bot),
        "end": list(p1_bot),
    }
    sketch["elements"].append(line_bot)

    return {
        "type": "slot",
        "arc_ids": [arc1["id"], arc2["id"]],
        "line_ids": [line_top["id"], line_bot["id"]],
        "center1": center1,
        "center2": center2,
        "radius": radius,
    }
