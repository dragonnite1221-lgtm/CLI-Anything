# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import _flatten_objects, load_scene  # noqa: E402,E501
from .scene_p14 import _diff_two_objects, _object_summary  # noqa: E402,E501
# fmt: on


def diff_scenes(scene_a_path: str, scene_b_path: str) -> Dict[str, Any]:
    """Structural diff between two scene files.

    Compares by GameObject Name (not GUID, since GUIDs differ across branches).
    Reports objects added in B, removed from B (that were in A), and objects
    whose summary or components differ.

    Returns:
        Dict with 'added' (list of names), 'removed' (list of names),
        'modified' (list of {name, changes}), 'identical' (bool), and
        'scene_property_changes' (dict of changed SceneProperties keys).
    """
    data_a = load_scene(scene_a_path)
    data_b = load_scene(scene_b_path)

    flat_a = _flatten_objects(data_a.get("GameObjects", []))
    flat_b = _flatten_objects(data_b.get("GameObjects", []))

    summary_a = {
        obj.get("Name", f"<unnamed:{i}>"): _object_summary(obj)
        for i, obj in enumerate(flat_a)
    }
    summary_b = {
        obj.get("Name", f"<unnamed:{i}>"): _object_summary(obj)
        for i, obj in enumerate(flat_b)
    }

    names_a = set(summary_a.keys())
    names_b = set(summary_b.keys())

    added = sorted(names_b - names_a)
    removed = sorted(names_a - names_b)
    modified: List[Dict[str, Any]] = []
    for name in sorted(names_a & names_b):
        d = _diff_two_objects(name, summary_a[name], summary_b[name])
        if d:
            modified.append(d)

    # Scene properties diff
    props_a = data_a.get("SceneProperties", {}) or {}
    props_b = data_b.get("SceneProperties", {}) or {}
    sp_changes: Dict[str, Any] = {}
    for k in set(props_a.keys()) | set(props_b.keys()):
        if props_a.get(k) != props_b.get(k):
            sp_changes[k] = {"from": props_a.get(k), "to": props_b.get(k)}

    identical = not (added or removed or modified or sp_changes)
    return {
        "scene_a": scene_a_path,
        "scene_b": scene_b_path,
        "added": added,
        "removed": removed,
        "modified": modified,
        "scene_property_changes": sp_changes,
        "identical": identical,
    }
