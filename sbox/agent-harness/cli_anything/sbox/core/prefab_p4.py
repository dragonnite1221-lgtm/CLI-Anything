# ruff: noqa: F403, F405, E501
from .prefab_base import *  # noqa: F403

# fmt: off
from .prefab_p1 import load_prefab, save_prefab  # noqa: E402,E501
# fmt: on


def modify_component(
    prefab_path: str,
    component_guid: Optional[str] = None,
    component_type: Optional[str] = None,
    object_guid: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Modify properties on a component within a prefab.

    Searches the RootObject and all children for a matching component. If
    *object_guid* is provided, the search is restricted to that GameObject;
    otherwise the first matching component anywhere in the tree wins.

    Returns dict with object_guid, component_guid, component_type, updated_keys.
    """
    if component_guid is None and component_type is None:
        raise ValueError("Must provide either component_guid or component_type")
    if not properties:
        raise ValueError("No properties specified to modify")

    data = load_prefab(prefab_path)
    root = data.get("RootObject")
    if root is None:
        raise ValueError("Prefab has no RootObject")

    all_objects: List[Dict[str, Any]] = [root]
    children = root.get("Children", [])
    if children:
        all_objects.extend(scene_mod._flatten_objects(children))

    # Optionally restrict to a single object
    if object_guid:
        all_objects = [o for o in all_objects if o.get("__guid") == object_guid]
        if not all_objects:
            raise ValueError(f"Object '{object_guid}' not found in prefab")

    target_obj = None
    target_comp = None
    for obj in all_objects:
        for comp in obj.get("Components", []):
            if component_guid and comp.get("__guid") == component_guid:
                target_obj, target_comp = obj, comp
                break
            if component_type and comp.get("__type") == component_type:
                target_obj, target_comp = obj, comp
                break
        if target_comp is not None:
            break

    if target_comp is None:
        identifier = component_guid or component_type
        raise ValueError(f"Component '{identifier}' not found in prefab")

    updated_keys = []
    for key, value in properties.items():
        target_comp[key] = value
        updated_keys.append(key)

    save_prefab(prefab_path, data)

    return {
        "object_guid": target_obj.get("__guid", ""),
        "component_guid": target_comp.get("__guid", ""),
        "component_type": target_comp.get("__type", ""),
        "updated_keys": updated_keys,
    }
