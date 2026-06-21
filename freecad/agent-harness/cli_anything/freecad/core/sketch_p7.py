# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_ellipse(
    project: Dict[str, Any],
    sketch_index: int,
    center: Optional[List[float]] = None,
    major_radius: float = 10.0,
    minor_radius: float = 5.0,
    angle: float = 0.0,
) -> Dict[str, Any]:
    """Add an ellipse element to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    center:
        Center point ``[x, y]``.  Defaults to ``[0, 0]``.
    major_radius:
        Semi-major axis length.  Must be positive.
    minor_radius:
        Semi-minor axis length.  Must be positive.
    angle:
        Rotation angle of the major axis in degrees.

    Returns
    -------
    Dict[str, Any]
        The newly created ellipse element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    center = _validate_point_2d(center if center is not None else [0, 0], "center")
    major_radius = float(major_radius)
    minor_radius = float(minor_radius)
    angle = float(angle)

    if major_radius <= 0:
        raise ValueError(f"Major radius must be positive, got {major_radius}")
    if minor_radius <= 0:
        raise ValueError(f"Minor radius must be positive, got {minor_radius}")
    if minor_radius > major_radius:
        raise ValueError(
            f"Minor radius ({minor_radius}) cannot exceed major radius ({major_radius})"
        )

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "ellipse",
        "center": center,
        "major_radius": major_radius,
        "minor_radius": minor_radius,
        "angle": angle,
    }

    sketch["elements"].append(element)
    return element
