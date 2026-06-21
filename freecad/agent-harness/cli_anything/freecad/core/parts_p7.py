# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def thickness_part(
    project: Dict[str, Any],
    index: int,
    thickness: float,
    faces: str = "all",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Hollow a solid by applying a wall *thickness*.

    Parameters
    ----------
    thickness : float
        Wall thickness value.
    faces : str
        Which faces to open — ``"all"`` or a comma-separated list of
        face indices (e.g. ``"0,2,5"``).
    """
    source = get_part(project, index)

    try:
        thick = float(thickness)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"thickness must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_thickness"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "thickness",
        "params": {
            "original_id": source["id"],
            "thickness": thick,
            "faces": faces,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result


def compound_parts(
    project: Dict[str, Any],
    indices: List[int],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Group several parts into a compound.

    The source parts are marked ``visible=False``; the compound is
    visible and stores references to its children by ID.

    Parameters
    ----------
    indices : list[int]
        Indices of the parts to group.
    """
    if not indices:
        raise ValueError("indices must be a non-empty list")

    child_ids: List[int] = []
    for idx in indices:
        part = get_part(project, idx)
        part["visible"] = False
        child_ids.append(part["id"])

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Compound"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "compound",
        "params": {
            "compound_children": child_ids,
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
