# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _next_id, _unique_name, _validate_vec3  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def scale_part(
    project: Dict[str, Any],
    index: int,
    factor: Union[float, List[float]],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a uniformly (or non-uniformly) scaled copy of a part.

    Parameters
    ----------
    factor : float or list[float]
        A single number for uniform scaling, or ``[sx, sy, sz]`` for
        per-axis scaling.
    """
    source = get_part(project, index)

    if isinstance(factor, (list, tuple)):
        scale_vec = _validate_vec3(factor, "factor")
    else:
        try:
            sf = float(factor)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"factor must be numeric: {exc}") from exc
        scale_vec = [sf, sf, sf]

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_scaled"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "scale",
        "params": {
            "original_id": source["id"],
            "scale": scale_vec,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result


def offset_shape(
    project: Dict[str, Any],
    index: int,
    distance: float,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an offset shell of the part at *index*.

    Parameters
    ----------
    distance : float
        Offset distance. Positive grows outward, negative shrinks inward.
    """
    source = get_part(project, index)

    try:
        dist = float(distance)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"distance must be numeric: {exc}") from exc

    if "parts" not in project:
        project["parts"] = []

    if name is None:
        base = f"{source['name']}_offset"
        name = _unique_name(project, base)

    result: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "type": "offset",
        "params": {
            "original_id": source["id"],
            "distance": dist,
        },
        "placement": deepcopy(source["placement"]),
        "material_index": source.get("material_index"),
        "visible": True,
    }

    project["parts"].append(result)
    return result
