# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def extrude_part(
    project: Dict[str, Any],
    index: int,
    direction: Optional[List[float]] = None,
    length: float = 10.0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Extrude the part at *index* along a direction vector.

    Parameters
    ----------
    direction : list[float] or None
        ``[dx, dy, dz]`` unit direction. Defaults to ``[0, 0, 1]``.
    length : float
        Extrusion length.
    """
    source = get_part(project, index)

    dir_vec = (
        _validate_vec3(direction, "direction")
        if direction is not None
        else [0.0, 0.0, 1.0]
    )

    try:
        lng = float(length)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"length must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_extrude"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "extrude",
        "params": {
            "original_id": source["id"],
            "direction": dir_vec,
            "length": lng,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result


def section_part(
    project: Dict[str, Any],
    index: int,
    plane: str = "XY",
    offset: float = 0.0,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a cross-section of the part at *index*.

    Parameters
    ----------
    plane : str
        Cutting plane — ``"XY"``, ``"XZ"``, or ``"YZ"``.
    offset : float
        Distance to shift the cutting plane along its normal.
    """
    valid_planes = {"XY", "XZ", "YZ"}
    if plane not in valid_planes:
        raise ValueError(
            f"Unknown section plane '{plane}'. Valid: {', '.join(sorted(valid_planes))}"
        )

    source = get_part(project, index)

    try:
        off = float(offset)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"offset must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_section"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "section",
        "params": {
            "original_id": source["id"],
            "plane": plane,
            "offset": off,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result
