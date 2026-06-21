# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import _new_guid  # noqa: E402,E501
from .scene_p5 import load_scene, save_scene  # noqa: E402,E501
from .scene_p6 import find_object  # noqa: E402,E501
# fmt: on


def modify_component(
    scene_path: str,
    object_guid: str,
    component_guid: Optional[str] = None,
    component_type: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Modify properties of an existing component on a GameObject.

    Finds the component by component_guid or component_type, then merges
    the provided properties onto it (only updates keys present in properties).

    Returns dict with object_guid, component_guid, component_type, and updated keys.
    Raises ValueError if object or component not found.
    """
    if component_guid is None and component_type is None:
        raise ValueError("Must provide either component_guid or component_type")
    if properties is None or len(properties) == 0:
        raise ValueError("No properties specified to modify")

    data = load_scene(scene_path)
    obj = find_object(data, guid=object_guid)
    if obj is None:
        raise ValueError(f"Object '{object_guid}' not found in scene")

    target_comp = None
    for comp in obj.get("Components", []):
        if component_guid and comp.get("__guid") == component_guid:
            target_comp = comp
            break
        if component_type and comp.get("__type") == component_type:
            target_comp = comp
            break

    if target_comp is None:
        identifier = component_guid or component_type
        raise ValueError(
            f"Component '{identifier}' not found on object '{object_guid}'"
        )

    updated_keys = []
    for key, value in properties.items():
        target_comp[key] = value
        updated_keys.append(key)

    save_scene(scene_path, data)

    return {
        "object_guid": object_guid,
        "component_guid": target_comp.get("__guid", ""),
        "component_type": target_comp.get("__type", ""),
        "updated_keys": updated_keys,
    }


def _regenerate_guids(obj: Dict[str, Any]) -> None:
    """Recursively regenerate all __guid fields in an object and its children/components."""
    if "__guid" in obj:
        obj["__guid"] = _new_guid()
    for comp in obj.get("Components", []):
        if "__guid" in comp:
            comp["__guid"] = _new_guid()
    for child in obj.get("Children", []):
        _regenerate_guids(child)
