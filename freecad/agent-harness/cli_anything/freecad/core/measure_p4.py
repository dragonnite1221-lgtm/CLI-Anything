# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _bbox_center, _compute_volume, _store_measurement  # noqa: E402,E501
from .measure_p2 import _compute_area  # noqa: E402,E501
# fmt: on


def measure_angle(
    project: Dict[str, Any],
    index1: int,
    index2: int,
    additive: bool = False,
) -> Dict[str, Any]:
    """Measure the angle between two parts based on their centre vectors from the origin.

    The angle is computed between the vectors from the world origin to
    each part's bounding-box centre.  Returns 0.0 when either vector is
    zero-length.

    Returns
    -------
    dict
        Measurement record with ``angle_deg`` value.
    """
    part1 = get_part(project, index1)
    part2 = get_part(project, index2)

    c1 = _bbox_center(part1)
    c2 = _bbox_center(part2)

    mag1 = math.sqrt(sum(v**2 for v in c1))
    mag2 = math.sqrt(sum(v**2 for v in c2))

    if mag1 == 0.0 or mag2 == 0.0:
        angle_deg = 0.0
    else:
        dot = sum(a * b for a, b in zip(c1, c2))
        cos_val = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        angle_deg = math.degrees(math.acos(cos_val))

    result_angle: Dict[str, Any] = {
        "part1_index": index1,
        "part2_index": index2,
        "angle_deg": round(angle_deg, 6),
    }
    if additive:
        result_angle["additive"] = True
    return _store_measurement(project, "angle", result_angle)


def measure_area(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Estimate the surface area of a part from its primitive parameters.

    Returns
    -------
    dict
        Measurement record with ``area`` value (or *None* for unsupported types).
    """
    part = get_part(project, index)
    area = _compute_area(part)

    result_area: Dict[str, Any] = {
        "part_index": index,
        "area": round(area, 6) if area is not None else None,
        "deferred": area is None,
    }
    if additive:
        result_area["additive"] = True
    return _store_measurement(project, "area", result_area)


def measure_volume(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Estimate the volume of a part from its primitive parameters.

    Formulas used:
    - box: V = l * w * h
    - cylinder: V = pi * r^2 * h
    - sphere: V = 4/3 * pi * r^3
    - cone: V = 1/3 * pi * h * (r1^2 + r1*r2 + r2^2)
    - torus: V = 2 * pi^2 * R * r^2

    Returns
    -------
    dict
        Measurement record with ``volume`` value (or *None* for unsupported types).
    """
    part = get_part(project, index)
    volume = _compute_volume(part)

    result_vol: Dict[str, Any] = {
        "part_index": index,
        "volume": round(volume, 6) if volume is not None else None,
        "deferred": volume is None,
    }
    if additive:
        result_vol["additive"] = True
    return _store_measurement(project, "volume", result_vol)
