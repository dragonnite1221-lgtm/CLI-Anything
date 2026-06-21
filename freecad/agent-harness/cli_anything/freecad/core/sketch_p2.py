# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _next_element_id, _validate_point_2d, _validate_project  # noqa: E402,E501
# fmt: on


def add_line(
    project: Dict[str, Any],
    sketch_index: int,
    start: Optional[List[float]] = None,
    end: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a line element to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch in ``project["sketches"]``.
    start:
        Start point ``[x, y]``.  Defaults to ``[0, 0]``.
    end:
        End point ``[x, y]``.  Defaults to ``[10, 0]``.

    Returns
    -------
    Dict[str, Any]
        The newly created line element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    start = _validate_point_2d(start if start is not None else [0, 0], "start")
    end = _validate_point_2d(end if end is not None else [10, 0], "end")

    if start == end:
        raise ValueError("Line start and end points must be different")

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "line",
        "start": start,
        "end": end,
    }

    sketch["elements"].append(element)
    return element


def add_circle(
    project: Dict[str, Any],
    sketch_index: int,
    center: Optional[List[float]] = None,
    radius: float = 5.0,
) -> Dict[str, Any]:
    """Add a circle element to a sketch.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.
    center:
        Center point ``[x, y]``.  Defaults to ``[0, 0]``.
    radius:
        Circle radius.  Must be positive.

    Returns
    -------
    Dict[str, Any]
        The newly created circle element.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    if sketch["closed"]:
        raise ValueError("Cannot add elements to a closed sketch")

    center = _validate_point_2d(center if center is not None else [0, 0], "center")
    radius = float(radius)
    if radius <= 0:
        raise ValueError(f"Radius must be positive, got {radius}")

    element: Dict[str, Any] = {
        "id": _next_element_id(sketch),
        "type": "circle",
        "center": center,
        "radius": radius,
    }

    sketch["elements"].append(element)
    return element
