# ruff: noqa: F403, F405, E501
from .prefab_base import *  # noqa: F403

# fmt: off
from .prefab_p1 import _write_json, load_prefab  # noqa: E402,E501
# fmt: on


def get_prefab_info(prefab_path: str) -> Dict[str, Any]:
    """Return dict with prefab metadata."""
    data = load_prefab(prefab_path)
    root = data.get("RootObject", {})
    components = root.get("Components", [])
    children = root.get("Children", [])

    # Gather all component types from root and children (flat)
    all_objects = [root]
    flat_children = scene_mod._flatten_objects(children)
    all_objects.extend(flat_children)

    component_types: set = set()
    total_components = 0
    for obj in all_objects:
        for comp in obj.get("Components", []):
            ctype = comp.get("__type", "")
            if ctype:
                component_types.add(ctype)
            total_components += 1

    return {
        "name": root.get("Name", ""),
        "guid": root.get("__guid", ""),
        "path": prefab_path,
        "component_count": total_components,
        "component_types": sorted(component_types),
        "children_count": len(flat_children),
        "network_mode": root.get("NetworkMode", 0),
    }


def from_scene_object(
    scene_path: str,
    object_guid: str,
    output_path: str,
) -> Dict[str, Any]:
    """Extract a GameObject from a scene and save as .prefab file.

    The GameObject (including its Components and Children) is copied into
    the prefab RootObject structure.  GUIDs are preserved from the scene.

    Returns the prefab data dict.
    """
    scene_data = scene_mod.load_scene(scene_path)
    obj = scene_mod.find_object(scene_data, guid=object_guid)
    if obj is None:
        raise ValueError(f"GameObject with guid '{object_guid}' not found in scene")

    # Build prefab from the scene object - copy it to avoid mutating the scene
    import copy

    root_object = copy.deepcopy(obj)

    # Ensure the root has the fields expected by the prefab format
    root_object.setdefault("Flags", 0)
    root_object.setdefault("Enabled", True)

    prefab: Dict[str, Any] = {
        "RootObject": root_object,
        "SceneProperties": {},
        "ResourceVersion": 1,
        "__references": [],
        "__version": 1,
    }

    _write_json(output_path, prefab)
    return prefab
