# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_bspline(
    project: Dict[str, Any],
    sketch_index: int,
    points: List[List[float]],
    closed: bool = False,
) -> Dict[str, Any]:
    """Add a B-spline element from control points to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    points:
        List of control points, each ``[x, y]``.  Minimum 2 points.
    closed:
        If ``True``, the B-spline forms a closed loop.

    Returns
    -------
    Dict[str, Any]
        The newly created B-spline element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("B-spline requires at least 2 control points")

    validated_points: List[List[float]] = []
    for i, pt in enumerate(points):
        validated_points.append(_validate_point_2d(pt, f"points[{i}]"))

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "bspline",
        "poles": validated_points,
        "closed": bool(closed),
    }

    sketch["elements"].append(element)
    return element
