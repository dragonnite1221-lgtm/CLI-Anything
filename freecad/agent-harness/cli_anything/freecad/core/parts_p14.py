# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_polygon_3d(
    project: Dict[str, Any],
    center: Optional[List[float]] = None,
    sides: int = 6,
    radius: float = 5.0,
    normal: Optional[List[float]] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a regular polygon in 3-D space.

    Parameters
    ----------
    center : list[float] or None
        ``[x, y, z]`` center point. Defaults to ``[0, 0, 0]``.
    sides : int
        Number of sides (>= 3).
    radius : float
        Circumscribed-circle radius.
    normal : list[float] or None
        ``[nx, ny, nz]`` plane normal. Defaults to ``[0, 0, 1]``.

    Returns the newly created part.
    """
    c = _validate_vec3(center, "center") if center is not None else [0.0, 0.0, 0.0]
    n = _validate_vec3(normal, "normal") if normal is not None else [0.0, 0.0, 1.0]

    if not isinstance(sides, int) or sides < 3:
        raise ValueError(f"sides must be an integer >= 3, got {sides}")

    try:
        rad = float(radius)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"radius must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Polygon3D"
        name = _unique_name(project, base)

    part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "polygon_3d",
        "params": {
            "center": c,
            "sides": float(sides),
            "radius": rad,
            "normal": n,
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
