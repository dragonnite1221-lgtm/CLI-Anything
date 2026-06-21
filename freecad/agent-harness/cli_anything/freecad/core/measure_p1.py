# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403


def _next_measurement_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for measurements."""
    items = project.get("measurements", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _store_measurement(
    project: Dict[str, Any],
    kind: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Wrap *result* in a measurement record and append to the project."""
    measurements = ensure_collection(project, "measurements")
    record: Dict[str, Any] = {
        "id": _next_measurement_id(project),
        "kind": kind,
        **result,
    }
    measurements.append(record)
    return record


def _get_position(part: Dict[str, Any]) -> List[float]:
    """Return the placement position of a part as ``[x, y, z]``."""
    return list(part["placement"]["position"])


def _bbox_center(part: Dict[str, Any]) -> List[float]:
    """Estimate the bounding-box centre of a part from its position and params."""
    pos = _get_position(part)
    p = part["params"]
    t = part["type"]

    if t == "box":
        return [
            pos[0] + p["length"] / 2.0,
            pos[1] + p["width"] / 2.0,
            pos[2] + p["height"] / 2.0,
        ]
    elif t == "cylinder":
        r = p["radius"]
        return [
            pos[0] + r,
            pos[1] + r,
            pos[2] + p["height"] / 2.0,
        ]
    elif t == "sphere":
        r = p["radius"]
        return [pos[0] + r, pos[1] + r, pos[2] + r]
    elif t == "cone":
        r = max(p["radius1"], p["radius2"])
        return [
            pos[0] + r,
            pos[1] + r,
            pos[2] + p["height"] / 2.0,
        ]
    elif t == "torus":
        R = p["radius1"]
        r = p["radius2"]
        return [
            pos[0] + R + r,
            pos[1] + R + r,
            pos[2] + r,
        ]
    elif t == "wedge":
        return [
            pos[0] + (p["xmin"] + p["xmax"]) / 2.0,
            pos[1] + (p["ymin"] + p["ymax"]) / 2.0,
            pos[2] + (p["zmin"] + p["zmax"]) / 2.0,
        ]
    # Boolean or unknown — fall back to placement position
    return pos


def _compute_volume(part: Dict[str, Any]) -> Optional[float]:
    """Compute volume from primitive parameters. Returns *None* for unknowns."""
    p = part["params"]
    t = part["type"]

    if t == "box":
        return p["length"] * p["width"] * p["height"]
    elif t == "cylinder":
        return math.pi * p["radius"] ** 2 * p["height"]
    elif t == "sphere":
        return (4.0 / 3.0) * math.pi * p["radius"] ** 3
    elif t == "cone":
        r1, r2, h = p["radius1"], p["radius2"], p["height"]
        return (1.0 / 3.0) * math.pi * h * (r1**2 + r1 * r2 + r2**2)
    elif t == "torus":
        R, r = p["radius1"], p["radius2"]
        return 2.0 * math.pi**2 * R * r**2
    elif t == "wedge":
        # Approximate as bounding box (exact wedge needs more info)
        dx = p["xmax"] - p["xmin"]
        dy = p["ymax"] - p["ymin"]
        dz = p["zmax"] - p["zmin"]
        return dx * dy * dz
    return None
