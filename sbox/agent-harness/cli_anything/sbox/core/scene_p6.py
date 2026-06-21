# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import _flatten_objects, load_scene  # noqa: E402,E501
# fmt: on


def get_scene_info(scene_path: str) -> Dict[str, Any]:
    """Return dict with scene metadata and object summary."""
    data = load_scene(scene_path)
    props = data.get("SceneProperties", {})
    objects = data.get("GameObjects", [])
    flat = _flatten_objects(objects)

    # Gather unique component types
    component_types: set = set()
    for obj in flat:
        for comp in obj.get("Components", []):
            ctype = comp.get("__type", "")
            if ctype:
                component_types.add(ctype)

    return {
        "title": data.get("Title", ""),
        "description": data.get("Description", ""),
        "path": scene_path,
        "fixed_update_freq": props.get("FixedUpdateFrequency"),
        "network_freq": props.get("NetworkFrequency"),
        "object_count": len(flat),
        "top_level_objects": len(objects),
        "component_types": sorted(component_types),
    }


def list_objects(scene_path: str) -> List[Dict[str, Any]]:
    """Return list of dicts with each GameObject's guid, name, position, component types."""
    data = load_scene(scene_path)
    flat = _flatten_objects(data.get("GameObjects", []))
    result: List[Dict[str, Any]] = []
    for obj in flat:
        comp_types = [
            c.get("__type", "") for c in obj.get("Components", []) if c.get("__type")
        ]
        result.append(
            {
                "guid": obj.get("__guid", ""),
                "name": obj.get("Name", ""),
                "position": obj.get("Position", "0,0,0"),
                "component_types": comp_types,
            }
        )
    return result


def find_object(
    scene_data: Dict[str, Any],
    name: Optional[str] = None,
    guid: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Find a GameObject by name or guid in scene data. Returns the object dict or None."""
    objects = scene_data.get("GameObjects", [])
    flat = _flatten_objects(objects)
    for obj in flat:
        if guid and obj.get("__guid") == guid:
            return obj
        if name and obj.get("Name") == name:
            return obj
    return None
