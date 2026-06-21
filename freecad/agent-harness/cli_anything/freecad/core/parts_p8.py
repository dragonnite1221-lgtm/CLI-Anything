# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def explode_compound(
    project: Dict[str, Any],
    index: int,
) -> List[Dict[str, Any]]:
    """Break a compound back into its individual child parts.

    The compound part is marked ``visible=False`` and each child part
    is restored to ``visible=True``.

    Returns the list of (now visible) child part dictionaries.
    """
    compound = get_part(project, index)
    if compound.get("type") != "compound":
        raise ValueError(
            f"Part at index {index} is not a compound (type='{compound.get('type')}')"
        )

    compound["visible"] = False

    child_ids = set(compound["params"].get("compound_children", []))
    restored: List[Dict[str, Any]] = []
    for part in project.get("parts", []):
        if part["id"] in child_ids:
            part["visible"] = True
            restored.append(part)

    return restored


def fillet_3d(
    project: Dict[str, Any],
    index: int,
    radius: float,
    edges: str = "all",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply a Part-level 3-D fillet to the part at *index*.

    Parameters
    ----------
    radius : float
        Fillet radius.
    edges : str
        Which edges to fillet — ``"all"`` or a comma-separated list of
        edge indices.
    """
    source = get_part(project, index)

    try:
        rad = float(radius)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"radius must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_fillet3d"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "fillet_3d",
        "params": {
            "original_id": source["id"],
            "radius": rad,
            "edges": edges,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result
