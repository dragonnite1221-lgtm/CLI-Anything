# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def copy_part(
    project: Dict[str, Any],
    index: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Deep-copy the part at *index* and append the copy to the project.

    The copy receives a new unique ``id`` and (optionally) a new *name*.
    All other attributes — parameters, placement, material — are duplicated.

    Returns the newly created part dictionary.
    """
    source = get_part(project, index)
    new_part: Dict[str, Any] = deepcopy(source)
    new_part["id"] = _next_id(project)

    if name is None:
        base = f"{source['name']}_copy"
        name = _unique_name(project, base)
    new_part["name"] = name

    project["parts"].append(new_part)
    return new_part


def mirror_part(
    project: Dict[str, Any],
    index: int,
    plane: str = "XY",
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a mirrored copy of the part at *index*.

    Parameters
    ----------
    plane : str
        Mirror plane — one of ``"XY"``, ``"XZ"``, or ``"YZ"``.
    name : str or None
        Label for the result. Auto-generated when *None*.

    Returns the newly created mirror part.
    """
    valid_planes = {"XY", "XZ", "YZ"}
    if plane not in valid_planes:
        raise ValueError(
            f"Unknown mirror plane '{plane}'. Valid: {', '.join(sorted(valid_planes))}"
        )

    source = get_part(project, index)

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_mirror"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "mirror",
        "params": {
            "original_id": source["id"],
            "mirror_plane": plane,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result
