# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def chamfer_3d(
    project: Dict[str, Any],
    index: int,
    size: float,
    edges: str = "all",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply a Part-level 3-D chamfer to the part at *index*.

    Parameters
    ----------
    size : float
        Chamfer size (distance).
    edges : str
        Which edges to chamfer — ``"all"`` or a comma-separated list of
        edge indices.
    """
    source = get_part(project, index)

    try:
        sz = float(size)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"size must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_chamfer3d"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "chamfer_3d",
        "params": {
            "original_id": source["id"],
            "size": sz,
            "edges": edges,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result


def loft_parts(
    project: Dict[str, Any],
    section_indices: List[int],
    solid: bool = True,
    ruled: bool = False,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Loft through a series of cross-section parts.

    Parameters
    ----------
    section_indices : list[int]
        Ordered indices of the profile/section parts.
    solid : bool
        Whether to create a solid (True) or a shell (False).
    ruled : bool
        Whether to use ruled surfaces between sections.
    """
    if len(section_indices) < 2:
        raise ValueError("loft requires at least 2 section indices")

    section_ids: List[int] = []
    for idx in section_indices:
        part = get_part(project, idx)
        section_ids.append(part["id"])

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = "Loft"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "loft",
        "params": {
            "section_ids": section_ids,
            "solid": solid,
            "ruled": ruled,
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
