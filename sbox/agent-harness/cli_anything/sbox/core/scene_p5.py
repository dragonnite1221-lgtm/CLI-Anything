# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p4 import _build_default_objects  # noqa: E402,E501
# fmt: on


def _flatten_objects(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recursively flatten a hierarchy of GameObjects into a flat list."""
    result: List[Dict[str, Any]] = []
    for obj in objects:
        result.append(obj)
        children = obj.get("Children", [])
        if children:
            result.extend(_flatten_objects(children))
    return result


def _remove_from_list(
    objects: List[Dict[str, Any]],
    name: Optional[str] = None,
    guid: Optional[str] = None,
) -> bool:
    """Remove a GameObject from a list (including nested Children). Returns True if removed."""
    for i, obj in enumerate(objects):
        if (guid and obj.get("__guid") == guid) or (name and obj.get("Name") == name):
            objects.pop(i)
            return True
        children = obj.get("Children", [])
        if children and _remove_from_list(children, name=name, guid=guid):
            return True
    return False


def _write_json(path: str, data: Dict[str, Any]) -> None:
    """Write data as formatted JSON to path."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def create_scene(
    name: str = "minimal",
    output_path: Optional[str] = None,
    fixed_update_freq: int = 50,
    network_freq: int = 60,
    include_defaults: bool = True,
) -> Dict[str, Any]:
    """Create a new .scene file.

    If *include_defaults* is True, adds Sun, Skybox, Plane, and Camera
    GameObjects to the scene.

    Returns the scene data dict.
    """
    game_objects: List[Dict[str, Any]] = []
    if include_defaults:
        game_objects = _build_default_objects()

    scene: Dict[str, Any] = {
        "GameObjects": game_objects,
        "SceneProperties": {
            "FixedUpdateFrequency": fixed_update_freq,
            "MaxFixedUpdates": 5,
            "NetworkFrequency": network_freq,
            "NetworkInterpolation": True,
            "PhysicsSubSteps": 1,
            "ThreadedAnimation": True,
            "TimeScale": 1,
            "UseFixedUpdate": True,
        },
        "Title": name,
        "Description": "",
        "ResourceVersion": 1,
        "__references": [],
        "__version": 1,
    }

    if output_path:
        _write_json(output_path, scene)

    return scene


def load_scene(scene_path: str) -> Dict[str, Any]:
    """Load and return parsed scene JSON."""
    with open(scene_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scene(scene_path: str, data: Dict[str, Any]) -> None:
    """Save scene JSON with proper formatting."""
    _write_json(scene_path, data)
