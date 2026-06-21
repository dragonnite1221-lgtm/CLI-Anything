# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_arc(
    project: Dict[str, Any],
    sketch_index: int,
    center: Optional[List[float]] = None,
    radius: float = 5.0,
    start_angle: float = 0.0,
    end_angle: float = 90.0,
) -> Dict[str, Any]:
    """Add an arc element to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    center:
        Center point ``[x, y]``.  Defaults to ``[0, 0]``.
    radius:
        Arc radius.  Must be positive.
    start_angle:
        Start angle in degrees.
    end_angle:
        End angle in degrees.  Must differ from *start_angle*.

    Returns
    -------
    Dict[str, Any]
        The newly created arc element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    center = _validate_point_2d(center if center is not None else [0, 0], "center")
    radius = float(radius)
    start_angle = float(start_angle)
    end_angle = float(end_angle)

    if radius <= 0:
        raise ValueError(f"Radius must be positive, got {radius}")
    if start_angle == end_angle:
        raise ValueError("Start angle and end angle must be different")

    # Compute start/end points for reference
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    start_point = [
        center[0] + radius * math.cos(start_rad),
        center[1] + radius * math.sin(start_rad),
    ]
    end_point = [
        center[0] + radius * math.cos(end_rad),
        center[1] + radius * math.sin(end_rad),
    ]

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "arc",
        "center": center,
        "radius": radius,
        "start_angle": start_angle,
        "end_angle": end_angle,
        "start_point": start_point,
        "end_point": end_point,
    }

    sketch["elements"].append(element)
    return element
