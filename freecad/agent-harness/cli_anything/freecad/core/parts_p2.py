# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _bbox_from_points, _transform_point, _validate_vec3  # noqa: E402,E501
# fmt: on


def _local_bounds(
    part_type: str, params: Dict[str, Any]
) -> Optional[Dict[str, Dict[str, float]]]:
    """Return a primitive-local bounding box for supported part types."""
    if part_type == "box":
        return {
            "min": {"x": 0.0, "y": 0.0, "z": 0.0},
            "max": {
                "x": float(params["length"]),
                "y": float(params["width"]),
                "z": float(params["height"]),
            },
        }

    if part_type == "cylinder":
        radius = float(params["radius"])
        height = float(params["height"])
        return {
            "min": {"x": -radius, "y": -radius, "z": 0.0},
            "max": {"x": radius, "y": radius, "z": height},
        }

    if part_type == "sphere":
        radius = float(params["radius"])
        return {
            "min": {"x": -radius, "y": -radius, "z": -radius},
            "max": {"x": radius, "y": radius, "z": radius},
        }

    if part_type == "cone":
        radius = max(float(params["radius1"]), float(params["radius2"]))
        height = float(params["height"])
        return {
            "min": {"x": -radius, "y": -radius, "z": 0.0},
            "max": {"x": radius, "y": radius, "z": height},
        }

    if part_type == "torus":
        radius1 = float(params["radius1"])
        radius2 = float(params["radius2"])
        major = radius1 + radius2
        return {
            "min": {"x": -major, "y": -major, "z": -radius2},
            "max": {"x": major, "y": major, "z": radius2},
        }

    if part_type == "wedge":
        return {
            "min": {
                "x": min(float(params["xmin"]), float(params["x2min"])),
                "y": float(params["ymin"]),
                "z": min(float(params["zmin"]), float(params["z2min"])),
            },
            "max": {
                "x": max(float(params["xmax"]), float(params["x2max"])),
                "y": float(params["ymax"]),
                "z": max(float(params["zmax"]), float(params["z2max"])),
            },
        }

    if part_type == "plane":
        return {
            "min": {"x": 0.0, "y": 0.0, "z": 0.0},
            "max": {
                "x": float(params["length"]),
                "y": float(params["width"]),
                "z": 0.0,
            },
        }

    if part_type == "polygon_3d":
        radius = float(params["radius"])
        return {
            "min": {"x": -radius, "y": -radius, "z": 0.0},
            "max": {"x": radius, "y": radius, "z": 0.0},
        }

    return None


def _world_bounds(part: Dict[str, Any]) -> Optional[Dict[str, Dict[str, float]]]:
    """Return a world-space bounding box for supported primitive parts."""
    local = _local_bounds(str(part.get("type", "")).lower(), part.get("params", {}))
    if local is None:
        return None

    min_corner = local["min"]
    max_corner = local["max"]
    corners = []
    for x in (min_corner["x"], max_corner["x"]):
        for y in (min_corner["y"], max_corner["y"]):
            for z in (min_corner["z"], max_corner["z"]):
                corners.append([x, y, z])

    placement = part.get("placement", {})
    position = _validate_vec3(placement.get("position", [0.0, 0.0, 0.0]), "position")
    rotation = _validate_vec3(placement.get("rotation", [0.0, 0.0, 0.0]), "rotation")
    return _bbox_from_points(
        [_transform_point(point, rotation, position) for point in corners]
    )


def _anchor_value(bounds: Dict[str, Dict[str, float]], axis: str, anchor: str) -> float:
    """Resolve an axis anchor string against a bounds payload."""
    aliases = {
        "min": "min",
        "max": "max",
        "center": "center",
        "left": "min",
        "right": "max",
        "bottom": "min",
        "top": "max",
        "front": "min",
        "back": "max",
        "mid": "center",
    }
    normalized = aliases.get(anchor.lower())
    if normalized is None:
        raise ValueError(f"Unknown anchor '{anchor}'. Valid: min, center, max")
    return float(bounds[normalized][axis])
