# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_line_3d(
    project: Dict[str, Any],
    start: Optional[List[float]] = None,
    end: Optional[List[float]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a 3-D line (edge) between two points.

    Parameters
    ----------
    start : list[float] or None
        ``[x, y, z]`` start point. Defaults to ``[0, 0, 0]``.
    end : list[float] or None
        ``[x, y, z]`` end point. Defaults to ``[10, 0, 0]``.

    Returns the newly created part.
    """
    s = _validate_vec3(start, "start") if start is not None else [0.0, 0.0, 0.0]
    e = _validate_vec3(end, "end") if end is not None else [10.0, 0.0, 0.0]

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Line3D"
        name = _unique_name(project, base)

    part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "line_3d",
        "params": {
            "start": s,
            "end": e,
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    project["parts"].append(part)
    return part


def add_wire(
    project: Dict[str, Any],
    points: List[List[float]],
    closed: bool = False,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a wire (polyline) from a list of ``[x, y, z]`` points.

    Parameters
    ----------
    points : list[list[float]]
        Ordered vertices. Must contain at least 2 points.
    closed : bool
        If *True* the wire forms a closed loop.

    Returns the newly created part.
    """
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("points must be a list of at least 2 [x,y,z] vertices")

    validated: List[List[float]] = []
    for i, pt in enumerate(points):
        validated.append(_validate_vec3(pt, f"points[{i}]"))

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Wire"
        name = _unique_name(project, base)

    part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "wire",
        "params": {
            "points": validated,
            "closed": closed,
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    project["parts"].append(part)
    return part
