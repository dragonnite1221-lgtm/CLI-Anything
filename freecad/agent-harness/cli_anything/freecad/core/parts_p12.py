# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def slice_part(
    project: Dict[str, Any],
    index: int,
    plane: str = "XY",
    offset: float = 0.0,
) -> Dict[str, Any]:
    """Slice the part at *index* into two halves along a plane.

    The original part is marked ``visible=False`` and two new parts are
    created — one for each side of the cutting plane.

    Returns a dict with keys ``"positive"`` and ``"negative"``, each
    holding the newly created part dictionary, plus ``"positive_index"``
    and ``"negative_index"`` with their list positions.
    """
    valid_planes = {"XY", "XZ", "YZ"}
    if plane not in valid_planes:
        raise ValueError(
            f"Unknown slice plane '{plane}'. Valid: {', '.join(sorted(valid_planes))}"
        )

    source = get_part(project, index)

    try:
        off = float(offset)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"offset must be numeric: {exc}") from exc

    source["visible"] = False

    if "parts" not in project:
        project["parts"] = []

    pos_name = _unique_name(project, f"{source['name']}_slice_pos")
    pos_part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": pos_name,
        "type": "slice",
        "params": {
            "original_id": source["id"],
            "plane": plane,
            "offset": off,
            "side": "positive",
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }
    project["parts"].append(pos_part)
    pos_index = len(project["parts"]) - 1

    neg_name = _unique_name(project, f"{source['name']}_slice_neg")
    neg_part: Dict[str, Any] = {
        "id": _next_id(project),
        "name": neg_name,
        "type": "slice",
        "params": {
            "original_id": source["id"],
            "plane": plane,
            "offset": off,
            "side": "negative",
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }
    project["parts"].append(neg_part)
    neg_index = len(project["parts"]) - 1

    return {
        "positive": pos_part,
        "negative": neg_part,
        "positive_index": pos_index,
        "negative_index": neg_index,
    }
