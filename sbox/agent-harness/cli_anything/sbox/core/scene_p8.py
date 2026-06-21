# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import load_scene, save_scene  # noqa: E402,E501
from .scene_p6 import find_object  # noqa: E402,E501
# fmt: on


def remove_component(
    scene_path: str,
    object_guid: str,
    component_guid: Optional[str] = None,
    component_type: Optional[str] = None,
) -> bool:
    """Remove a component from a GameObject by guid or type.

    Returns True if a component was removed.
    """
    if not component_guid and not component_type:
        raise ValueError("Must specify either component_guid or component_type")

    data = load_scene(scene_path)
    obj = find_object(data, guid=object_guid)
    if obj is None:
        raise ValueError(f"GameObject with guid '{object_guid}' not found")

    components = obj.get("Components", [])
    for i, comp in enumerate(components):
        if component_guid and comp.get("__guid") == component_guid:
            components.pop(i)
            save_scene(scene_path, data)
            return True
        if component_type and comp.get("__type") == component_type:
            components.pop(i)
            save_scene(scene_path, data)
            return True

    return False


def modify_object(
    scene_path: str,
    guid: Optional[str] = None,
    name_match: Optional[str] = None,
    new_name: Optional[str] = None,
    position: Optional[str] = None,
    rotation: Optional[str] = None,
    scale: Optional[str] = None,
    tags: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """Modify properties of an existing GameObject in a scene.

    Finds the object by guid or name_match, then updates only the fields
    that are explicitly provided (non-None).

    Returns dict with guid, name, and list of modified_fields.
    Raises ValueError if object not found or no identifier given.
    """
    if guid is None and name_match is None:
        raise ValueError(
            "Must provide either guid or name_match to identify the object"
        )

    data = load_scene(scene_path)
    obj = find_object(data, name=name_match, guid=guid)
    if obj is None:
        identifier = guid or name_match
        raise ValueError(f"Object '{identifier}' not found in scene")

    modified_fields = []

    if new_name is not None:
        obj["Name"] = new_name
        modified_fields.append("Name")
    if position is not None:
        obj["Position"] = position
        modified_fields.append("Position")
    if rotation is not None:
        obj["Rotation"] = rotation
        modified_fields.append("Rotation")
    if scale is not None:
        obj["Scale"] = scale
        modified_fields.append("Scale")
    if tags is not None:
        obj["Tags"] = tags
        modified_fields.append("Tags")
    if enabled is not None:
        obj["Enabled"] = enabled
        modified_fields.append("Enabled")

    save_scene(scene_path, data)

    return {
        "guid": obj["__guid"],
        "name": obj["Name"],
        "modified_fields": modified_fields,
    }


_SCENE_PROPERTY_MAP: Dict[str, str] = {
    "fixed_update_freq": "FixedUpdateFrequency",
    "max_fixed_updates": "MaxFixedUpdates",
    "network_freq": "NetworkFrequency",
    "network_interpolation": "NetworkInterpolation",
    "physics_sub_steps": "PhysicsSubSteps",
    "threaded_animation": "ThreadedAnimation",
    "timescale": "TimeScale",
    "use_fixed_update": "UseFixedUpdate",
}
