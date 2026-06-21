# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import load_scene, save_scene  # noqa: E402,E501
from .scene_p8 import _SCENE_PROPERTY_MAP  # noqa: E402,E501
# fmt: on


def set_scene_properties(
    scene_path: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Modify SceneProperties of a scene file.

    Accepts keyword arguments matching the keys in _SCENE_PROPERTY_MAP.
    Only updates properties that are explicitly provided.

    Returns the updated SceneProperties dict.
    """
    data = load_scene(scene_path)
    props = data.get("SceneProperties", {})

    updated = []
    for kwarg_key, value in kwargs.items():
        json_key = _SCENE_PROPERTY_MAP.get(kwarg_key)
        if json_key is None:
            raise ValueError(f"Unknown scene property: '{kwarg_key}'")
        props[json_key] = value
        updated.append(json_key)

    data["SceneProperties"] = props
    save_scene(scene_path, data)

    return props


_NAVMESH_PROPERTY_MAP: Dict[str, str] = {
    "navmesh_enabled": "Enabled",
    "navmesh_include_static": "IncludeStaticBodies",
    "navmesh_include_keyframed": "IncludeKeyframedBodies",
    "navmesh_agent_height": "AgentHeight",
    "navmesh_agent_radius": "AgentRadius",
    "navmesh_agent_step_size": "AgentStepSize",
    "navmesh_agent_max_slope": "AgentMaxSlope",
}


def set_navmesh_properties(
    scene_path: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Modify NavMesh properties of a scene file.

    Accepts keyword arguments matching _NAVMESH_PROPERTY_MAP keys.
    Returns the updated NavMesh properties dict.
    """
    data = load_scene(scene_path)
    props = data.get("SceneProperties", {})
    navmesh = props.get("NavMesh", {})

    for kwarg_key, value in kwargs.items():
        json_key = _NAVMESH_PROPERTY_MAP.get(kwarg_key)
        if json_key is None:
            raise ValueError(f"Unknown navmesh property: '{kwarg_key}'")
        navmesh[json_key] = value

    props["NavMesh"] = navmesh
    data["SceneProperties"] = props
    save_scene(scene_path, data)

    return navmesh
