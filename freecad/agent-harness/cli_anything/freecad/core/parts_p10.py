# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def sweep_part(
    project: Dict[str, Any],
    profile_index: int,
    path_index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Sweep a profile shape along a path shape.

    Parameters
    ----------
    profile_index : int
        Index of the profile (cross-section) part.
    path_index : int
        Index of the path (spine) part.
    """
    profile = get_part(project, profile_index)
    path = get_part(project, path_index)

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Sweep"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "sweep",
        "params": {
            "profile_id": profile["id"],
            "path_id": path["id"],
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    project["parts"].append(result)
    return result


def revolve_part(
    project: Dict[str, Any],
    index: int,
    axis: str = "Z",
    angle: float = 360.0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Revolve the part at *index* around an axis.

    Parameters
    ----------
    axis : str
        Axis of revolution — ``"X"``, ``"Y"``, or ``"Z"``.
    angle : float
        Revolution angle in degrees (default 360 for a full revolution).
    """
    valid_axes = {"X", "Y", "Z"}
    if axis not in valid_axes:
        raise ValueError(
            f"Unknown axis '{axis}'. Valid: {', '.join(sorted(valid_axes))}"
        )

    source = get_part(project, index)

    try:
        ang = float(angle)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"angle must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_revolve"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "revolve",
        "params": {
            "original_id": source["id"],
            "axis": axis,
            "angle": ang,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result
