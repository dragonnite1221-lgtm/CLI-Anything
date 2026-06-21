# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _bbox_center, _get_position, _store_measurement  # noqa: E402,E501
# fmt: on


def measure_center_of_mass(
    project: Dict[str, Any],
    index: int,
    additive: bool = False,
) -> Dict[str, Any]:
    """Estimate the centre of mass (geometric centre for simple shapes).

    For uniform-density primitives the centre of mass coincides with the
    bounding-box centre.

    Returns
    -------
    dict
        Measurement record with ``center_of_mass`` ``[x, y, z]``.
    """
    part = get_part(project, index)
    com = _bbox_center(part)

    result_com: Dict[str, Any] = {
        "part_index": index,
        "center_of_mass": [round(v, 6) for v in com],
    }
    if additive:
        result_com["additive"] = True
    return _store_measurement(project, "center_of_mass", result_com)


def measure_bounding_box(
    project: Dict[str, Any],
    index: int,
    additive: bool = False,
) -> Dict[str, Any]:
    """Compute the axis-aligned bounding box of a part.

    The bounding box is derived from the part's position and primitive
    parameters.

    Returns
    -------
    dict
        Measurement record with ``min``, ``max``, and ``size`` vectors.
    """
    part = get_part(project, index)
    pos = _get_position(part)
    p = part["params"]
    t = part["type"]

    if t == "box":
        bb_min = pos[:]
        bb_max = [
            pos[0] + p["length"],
            pos[1] + p["width"],
            pos[2] + p["height"],
        ]
    elif t == "cylinder":
        r = p["radius"]
        bb_min = [pos[0] - r, pos[1] - r, pos[2]]
        bb_max = [pos[0] + r, pos[1] + r, pos[2] + p["height"]]
    elif t == "sphere":
        r = p["radius"]
        bb_min = [pos[0] - r, pos[1] - r, pos[2] - r]
        bb_max = [pos[0] + r, pos[1] + r, pos[2] + r]
    elif t == "cone":
        r = max(p["radius1"], p["radius2"])
        bb_min = [pos[0] - r, pos[1] - r, pos[2]]
        bb_max = [pos[0] + r, pos[1] + r, pos[2] + p["height"]]
    elif t == "torus":
        R, r = p["radius1"], p["radius2"]
        outer = R + r
        bb_min = [pos[0] - outer, pos[1] - outer, pos[2] - r]
        bb_max = [pos[0] + outer, pos[1] + outer, pos[2] + r]
    elif t == "wedge":
        bb_min = [
            pos[0] + p["xmin"],
            pos[1] + p["ymin"],
            pos[2] + p["zmin"],
        ]
        bb_max = [
            pos[0] + p["xmax"],
            pos[1] + p["ymax"],
            pos[2] + p["zmax"],
        ]
    else:
        # Unknown / boolean — deferred
        result_bb_def: Dict[str, Any] = {
            "part_index": index,
            "min": None,
            "max": None,
            "size": None,
            "deferred": True,
        }
        if additive:
            result_bb_def["additive"] = True
        return _store_measurement(project, "bounding_box", result_bb_def)

    size = [bb_max[i] - bb_min[i] for i in range(3)]

    result_bb: Dict[str, Any] = {
        "part_index": index,
        "min": [round(v, 6) for v in bb_min],
        "max": [round(v, 6) for v in bb_max],
        "size": [round(v, 6) for v in size],
        "deferred": False,
    }
    if additive:
        result_bb["additive"] = True
    return _store_measurement(project, "bounding_box", result_bb)
