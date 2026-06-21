# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _get_position, _store_measurement  # noqa: E402,E501
# fmt: on


def measure_radius(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Return the radius of a cylindrical, spherical, or toroidal part.

    For cones, the larger of ``radius1`` / ``radius2`` is returned.

    Returns
    -------
    dict
        Measurement record with ``radius`` value.

    Raises
    ------
    ValueError
        If the part type has no meaningful radius.
    """
    part = get_part(project, index)
    p = part["params"]
    t = part["type"]

    if t == "cylinder":
        radius = p["radius"]
    elif t == "sphere":
        radius = p["radius"]
    elif t == "cone":
        radius = max(p["radius1"], p["radius2"])
    elif t == "torus":
        radius = p["radius2"]
    else:
        raise ValueError(
            f"Part type '{t}' has no meaningful radius. "
            f"Supported: cylinder, sphere, cone, torus"
        )

    result_rad: Dict[str, Any] = {
        "part_index": index,
        "radius": round(radius, 6),
    }
    if additive:
        result_rad["additive"] = True
    return _store_measurement(project, "radius", result_rad)


def measure_diameter(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Return the diameter of a cylindrical, spherical, or toroidal part.

    Returns
    -------
    dict
        Measurement record with ``diameter`` value.

    Raises
    ------
    ValueError
        If the part type has no meaningful diameter.
    """
    part = get_part(project, index)
    p = part["params"]
    t = part["type"]

    if t == "cylinder":
        diameter = 2.0 * p["radius"]
    elif t == "sphere":
        diameter = 2.0 * p["radius"]
    elif t == "cone":
        diameter = 2.0 * max(p["radius1"], p["radius2"])
    elif t == "torus":
        diameter = 2.0 * p["radius2"]
    else:
        raise ValueError(
            f"Part type '{t}' has no meaningful diameter. "
            f"Supported: cylinder, sphere, cone, torus"
        )

    result_dia: Dict[str, Any] = {
        "part_index": index,
        "diameter": round(diameter, 6),
    }
    if additive:
        result_dia["additive"] = True
    return _store_measurement(project, "diameter", result_dia)


def measure_position(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Return the placement position of a part.

    Returns
    -------
    dict
        Measurement record with ``position`` ``[x, y, z]``.
    """
    part = get_part(project, index)
    pos = _get_position(part)

    result_pos: Dict[str, Any] = {
        "part_index": index,
        "position": pos,
    }
    if additive:
        result_pos["additive"] = True
    return _store_measurement(project, "position", result_pos)
