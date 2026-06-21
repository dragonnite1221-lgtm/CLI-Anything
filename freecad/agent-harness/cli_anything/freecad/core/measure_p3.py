# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _bbox_center, _store_measurement  # noqa: E402,E501
# fmt: on


def measure_distance(
    project: Dict[str, Any],
    index1: int,
    index2: int,
    additive: bool = False,
) -> Dict[str, Any]:
    """Measure the Euclidean distance between two parts (bounding-box centres).

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index1 : int
        Index of the first part in ``project["parts"]``.
    index2 : int
        Index of the second part in ``project["parts"]``.

    Returns
    -------
    dict
        Measurement record with ``distance`` value and axis deltas.
    """
    part1 = get_part(project, index1)
    part2 = get_part(project, index2)

    c1 = _bbox_center(part1)
    c2 = _bbox_center(part2)

    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    dz = c2[2] - c1[2]
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    result: Dict[str, Any] = {
        "part1_index": index1,
        "part2_index": index2,
        "distance": round(dist, 6),
        "delta": [round(dx, 6), round(dy, 6), round(dz, 6)],
    }
    if additive:
        result["additive"] = True
    return _store_measurement(project, "distance", result)


def measure_length(
    project: Dict[str, Any],
    index: int,
    edge_ref: Optional[str] = None,
    additive: bool = False,
) -> Dict[str, Any]:
    """Estimate the length of a part edge.

    For primitives without an explicit *edge_ref*, the longest dimension
    is returned as an estimate.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the part in ``project["parts"]``.
    edge_ref : str or None
        Optional edge reference (e.g. ``"Edge1"``).  When supplied the
        measurement is stored as a deferred request.

    Returns
    -------
    dict
        Measurement record with ``length`` value.
    """
    part = get_part(project, index)
    p = part["params"]
    t = part["type"]
    length: Optional[float] = None

    if edge_ref is not None:
        # Deferred — requires macro execution
        result_deferred: Dict[str, Any] = {
            "part_index": index,
            "edge_ref": edge_ref,
            "length": None,
            "deferred": True,
        }
        if additive:
            result_deferred["additive"] = True
        return _store_measurement(project, "length", result_deferred)

    if t == "box":
        length = max(p["length"], p["width"], p["height"])
    elif t == "cylinder":
        length = p["height"]
    elif t == "sphere":
        length = 2.0 * p["radius"]
    elif t == "cone":
        length = p["height"]
    elif t == "torus":
        length = 2.0 * math.pi * p["radius1"]
    elif t == "wedge":
        length = max(
            p["xmax"] - p["xmin"],
            p["ymax"] - p["ymin"],
            p["zmax"] - p["zmin"],
        )

    result_len: Dict[str, Any] = {
        "part_index": index,
        "edge_ref": edge_ref,
        "length": round(length, 6) if length is not None else None,
        "deferred": length is None,
    }
    if additive:
        result_len["additive"] = True
    return _store_measurement(project, "length", result_len)
