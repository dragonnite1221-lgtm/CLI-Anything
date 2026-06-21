# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p2 import _make_component, _new_guid  # noqa: E402,E501
from .scene_p3 import _make_game_object  # noqa: E402,E501
from .scene_p5 import _remove_from_list, load_scene, save_scene  # noqa: E402,E501
from .scene_p6 import find_object  # noqa: E402,E501
# fmt: on


def add_object(
    scene_path: str,
    name: str,
    position: str = "0,0,0",
    rotation: str = "0,0,0,1",
    scale: str = "1,1,1",
    tags: str = "",
    components: Optional[List[Dict[str, Any]]] = None,
    parent_guid: Optional[str] = None,
) -> str:
    """Add a new GameObject to the scene.

    *components* is a list of component dicts. Each dict should have at least
    a ``__type`` key, or be a preset name string that will be resolved via
    COMPONENT_PRESETS.

    If *parent_guid* is specified, adds the object as a child of that parent.

    Returns the new object's guid.
    """
    data = load_scene(scene_path)

    # Resolve component specs
    resolved_components: List[Dict[str, Any]] = []
    if components:
        for comp in components:
            if isinstance(comp, str):
                resolved_components.append(_make_component(comp))
            elif isinstance(comp, dict):
                c = dict(comp)
                if "__guid" not in c:
                    c["__guid"] = _new_guid()
                resolved_components.append(c)

    obj = _make_game_object(
        name=name,
        position=position,
        rotation=rotation,
        scale=scale,
        tags=tags,
        components=resolved_components,
    )
    new_guid = obj["__guid"]

    if parent_guid:
        parent = find_object(data, guid=parent_guid)
        if parent is None:
            raise ValueError(f"Parent object with guid '{parent_guid}' not found")
        parent.setdefault("Children", []).append(obj)
    else:
        data.setdefault("GameObjects", []).append(obj)

    save_scene(scene_path, data)
    return new_guid


def remove_object(
    scene_path: str,
    name: Optional[str] = None,
    guid: Optional[str] = None,
) -> bool:
    """Remove a GameObject by name or guid. Returns True if removed."""
    if not name and not guid:
        raise ValueError("Must specify either name or guid")

    data = load_scene(scene_path)
    objects = data.get("GameObjects", [])
    removed = _remove_from_list(objects, name=name, guid=guid)
    if removed:
        save_scene(scene_path, data)
    return removed


def add_component(
    scene_path: str,
    object_guid: str,
    component_type: str,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
    """Add a component to a GameObject.

    *component_type* is either a preset name (e.g. ``"rigidbody"``) or a
    fully qualified type (e.g. ``"Sandbox.Rigidbody"``).

    *properties* is a dict of component properties to set/override.

    Returns the new component's guid.
    """
    data = load_scene(scene_path)
    obj = find_object(data, guid=object_guid)
    if obj is None:
        raise ValueError(f"GameObject with guid '{object_guid}' not found")

    comp = _make_component(component_type, properties)
    comp_guid = comp["__guid"]
    obj.setdefault("Components", []).append(comp)

    save_scene(scene_path, data)
    return comp_guid
