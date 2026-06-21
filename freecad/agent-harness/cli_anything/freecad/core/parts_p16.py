# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403

# fmt: off
from .parts_p1 import _validate_vec3  # noqa: E402,E501
from .parts_p2 import _anchor_value, _world_bounds  # noqa: E402,E501
from .parts_p3 import get_part  # noqa: E402,E501
from .parts_p15 import _estimate_geometry  # noqa: E402,E501
# fmt: on


def align_part(
    project: Dict[str, Any],
    index: int,
    target_index: int,
    *,
    x: Optional[str] = None,
    to_x: Optional[str] = None,
    dx: float = 0.0,
    y: Optional[str] = None,
    to_y: Optional[str] = None,
    dy: float = 0.0,
    z: Optional[str] = None,
    to_z: Optional[str] = None,
    dz: float = 0.0,
) -> Dict[str, Any]:
    """Move a part so selected bbox anchors match another part's anchors."""
    part = get_part(project, index)
    target = get_part(project, target_index)
    source_bounds = _world_bounds(part)
    target_bounds = _world_bounds(target)
    if source_bounds is None:
        raise ValueError(
            f"Part #{index} ({part['name']}) does not support bounding-box alignment for type '{part['type']}'"
        )
    if target_bounds is None:
        raise ValueError(
            f"Target part #{target_index} ({target['name']}) does not support bounding-box alignment for type '{target['type']}'"
        )

    updates = {
        "x": (x, to_x, float(dx)),
        "y": (y, to_y, float(dy)),
        "z": (z, to_z, float(dz)),
    }
    if not any(
        source_anchor or target_anchor
        for source_anchor, target_anchor, _ in updates.values()
    ):
        raise ValueError("At least one axis alignment must be specified")

    position = _validate_vec3(part["placement"]["position"], "position")
    delta = [0.0, 0.0, 0.0]
    axis_to_index = {"x": 0, "y": 1, "z": 2}

    for axis, (source_anchor, target_anchor, offset) in updates.items():
        if source_anchor is None and target_anchor is None:
            continue
        if source_anchor is None or target_anchor is None:
            raise ValueError(f"Axis '{axis}' requires both source and target anchors")
        shift = (
            _anchor_value(target_bounds, axis, target_anchor)
            + offset
            - _anchor_value(source_bounds, axis, source_anchor)
        )
        delta[axis_to_index[axis]] = shift
        position[axis_to_index[axis]] += shift

    part["placement"]["position"] = position
    updated_bounds = _world_bounds(part)
    return {
        "part_index": index,
        "target_index": target_index,
        "part_name": part["name"],
        "target_name": target["name"],
        "delta": {"x": delta[0], "y": delta[1], "z": delta[2]},
        "placement": deepcopy(part["placement"]),
        "world_bounding_box": updated_bounds,
    }


def part_info(
    project: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Return detailed information about the part at *index*.

    The returned dictionary includes:

    - ``type`` — the part type string.
    - ``params`` — a copy of the part's parameter dict.
    - ``placement`` — position and rotation.
    - ``material_index`` — index into the materials list (or *None*).
    - ``visible`` — visibility flag.
    - ``volume`` — estimated volume (or *None* if not computable).
    - ``area`` — estimated surface area (or *None*).
    - ``bounding_box`` — estimated axis-aligned bounding box ``{x, y, z}``
      (or *None*).
    """
    part = get_part(project, index)
    geo = _estimate_geometry(part["type"], part.get("params", {}))
    world = _world_bounds(part)

    return {
        "id": part["id"],
        "name": part["name"],
        "type": part["type"],
        "params": deepcopy(part["params"]),
        "placement": deepcopy(part["placement"]),
        "material_index": part.get("material_index"),
        "visible": part.get("visible", True),
        "volume": geo["volume"],
        "area": geo["area"],
        "bounding_box": geo["bounding_box"],
        "world_bounding_box": world,
    }
