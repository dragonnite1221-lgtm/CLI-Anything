# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import _flatten_objects, load_scene, save_scene  # noqa: E402,E501
from .scene_p12 import query_objects  # noqa: E402,E501
# fmt: on


def bulk_modify_objects(
    scene_path: str,
    has_component: Optional[str] = None,
    has_tag: Optional[str] = None,
    name_match: Optional[str] = None,
    name_regex: Optional[str] = None,
    in_bounds: Optional[str] = None,
    enabled_filter: Optional[bool] = None,
    new_position: Optional[str] = None,
    new_rotation: Optional[str] = None,
    new_scale: Optional[str] = None,
    new_tags: Optional[str] = None,
    new_enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """Apply the same modification to every GameObject matching the filters.

    Reads the scene once, runs the query, mutates each match in place, and
    writes the scene back. At least one ``new_*`` value must be provided.

    Returns:
        Dict with ``modified_count``, ``modified_fields``, and ``modified_guids``.
    """
    update_fields = {
        "Position": new_position,
        "Rotation": new_rotation,
        "Scale": new_scale,
        "Tags": new_tags,
        "Enabled": new_enabled,
    }
    active_updates = {k: v for k, v in update_fields.items() if v is not None}
    if not active_updates:
        raise ValueError(
            "Must provide at least one modification (new_position, new_rotation, etc.)"
        )

    matches = query_objects(
        scene_path,
        has_component=has_component,
        has_tag=has_tag,
        name_match=name_match,
        name_regex=name_regex,
        in_bounds=in_bounds,
        enabled=enabled_filter,
    )

    if not matches:
        return {
            "modified_count": 0,
            "modified_fields": list(active_updates.keys()),
            "modified_guids": [],
        }

    data = load_scene(scene_path)
    flat = _flatten_objects(data.get("GameObjects", []))
    by_guid = {obj.get("__guid"): obj for obj in flat}

    modified_guids: List[str] = []
    for match in matches:
        guid = match["guid"]
        obj = by_guid.get(guid)
        if obj is None:
            continue
        for key, value in active_updates.items():
            obj[key] = value
        modified_guids.append(guid)

    save_scene(scene_path, data)

    return {
        "modified_count": len(modified_guids),
        "modified_fields": list(active_updates.keys()),
        "modified_guids": modified_guids,
    }
