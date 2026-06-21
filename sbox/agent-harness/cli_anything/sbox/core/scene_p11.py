# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import COMPONENT_PRESETS  # noqa: E402,E501
from .scene_p5 import load_scene, save_scene  # noqa: E402,E501
from .scene_p6 import find_object  # noqa: E402,E501
from .scene_p10 import _regenerate_guids  # noqa: E402,E501
# fmt: on


def clone_object(
    scene_path: str,
    guid: Optional[str] = None,
    name: Optional[str] = None,
    new_name: Optional[str] = None,
    position: Optional[str] = None,
) -> Dict[str, Any]:
    """Clone (duplicate) a GameObject in a scene.

    Finds the original by guid or name, deep-copies it with new GUIDs,
    optionally renames and repositions the clone.

    Returns dict with the new object's guid and name.
    """
    import copy

    data = load_scene(scene_path)
    original = find_object(data, name=name, guid=guid)
    if original is None:
        identifier = guid or name
        raise ValueError(f"Object '{identifier}' not found in scene")

    clone = copy.deepcopy(original)

    # Regenerate all GUIDs in the clone
    _regenerate_guids(clone)

    if new_name is not None:
        clone["Name"] = new_name
    else:
        clone["Name"] = original["Name"] + " (Clone)"

    if position is not None:
        clone["Position"] = position

    # Add clone as top-level object
    data["GameObjects"].append(clone)
    save_scene(scene_path, data)

    return {
        "guid": clone["__guid"],
        "name": clone["Name"],
        "original_guid": original["__guid"],
        "original_name": original["Name"],
    }


def get_object(
    scene_path: str,
    guid: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Get full details of a single GameObject.

    Returns dict with guid, name, position, rotation, scale, tags, enabled,
    components (list of type + properties), and children count.
    Raises ValueError if not found.
    """
    data = load_scene(scene_path)
    obj = find_object(data, name=name, guid=guid)
    if obj is None:
        identifier = guid or name
        raise ValueError(f"Object '{identifier}' not found in scene")

    components = []
    for comp in obj.get("Components", []):
        c = {"guid": comp.get("__guid", ""), "type": comp.get("__type", "")}
        # Include all non-internal properties
        for k, v in comp.items():
            if not k.startswith("__"):
                c[k] = v
        components.append(c)

    return {
        "guid": obj.get("__guid", ""),
        "name": obj.get("Name", ""),
        "position": obj.get("Position", "0,0,0"),
        "rotation": obj.get("Rotation", "0,0,0,1"),
        "scale": obj.get("Scale", "1,1,1"),
        "tags": obj.get("Tags", ""),
        "enabled": obj.get("Enabled", True),
        "components": components,
        "children_count": len(obj.get("Children", [])),
    }


def _resolve_component_type(component: str) -> str:
    """Resolve a component preset name to its full Sandbox type, or pass through.

    Args:
        component: Either a preset key (e.g. "rigidbody") or a fully qualified
                   type (e.g. "Sandbox.Rigidbody" or "MyGame.MyComponent").

    Returns:
        The fully qualified type string.
    """
    if component in COMPONENT_PRESETS:
        return COMPONENT_PRESETS[component]["__type"]
    return component
