# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p2 import _local_bounds, _world_bounds  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
# fmt: on


def _estimate_geometry(part_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Compute estimated volume, surface area, and bounding box from params.

    Returns a dict with keys ``volume``, ``area``, and ``bounding_box``
    (each may be *None* when computation is not applicable).
    """
    volume: Optional[float] = None
    area: Optional[float] = None
    bbox: Optional[Dict[str, float]] = None

    if part_type == "box":
        l, w, h = params["length"], params["width"], params["height"]
        volume = l * w * h
        area = 2.0 * (l * w + w * h + l * h)
        bbox = {"x": l, "y": w, "z": h}

    elif part_type == "cylinder":
        r, h = params["radius"], params["height"]
        volume = math.pi * r * r * h
        area = 2.0 * math.pi * r * (r + h)
        bbox = {"x": 2 * r, "y": 2 * r, "z": h}

    elif part_type == "sphere":
        r = params["radius"]
        volume = (4.0 / 3.0) * math.pi * r**3
        area = 4.0 * math.pi * r**2
        bbox = {"x": 2 * r, "y": 2 * r, "z": 2 * r}

    elif part_type == "cone":
        r1, r2, h = params["radius1"], params["radius2"], params["height"]
        volume = math.pi * h / 3.0 * (r1**2 + r1 * r2 + r2**2)
        # Lateral + two caps
        slant = math.sqrt(h**2 + (r1 - r2) ** 2)
        area = math.pi * (r1 + r2) * slant + math.pi * r1**2 + math.pi * r2**2
        rmax = max(r1, r2)
        bbox = {"x": 2 * rmax, "y": 2 * rmax, "z": h}

    elif part_type == "torus":
        R, r = params["radius1"], params["radius2"]
        volume = 2.0 * math.pi**2 * R * r**2
        area = 4.0 * math.pi**2 * R * r
        bbox = {"x": 2 * (R + r), "y": 2 * (R + r), "z": 2 * r}

    return {
        "volume": volume,
        "area": area,
        "bounding_box": bbox,
    }


def part_bounds(
    project: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Return local and world bounding-box data for a part."""
    part = get_part(project, index)
    local = _local_bounds(str(part["type"]).lower(), part.get("params", {}))
    world = _world_bounds(part)
    return {
        "id": part["id"],
        "name": part["name"],
        "type": part["type"],
        "local_bounding_box": local,
        "world_bounding_box": world,
    }
