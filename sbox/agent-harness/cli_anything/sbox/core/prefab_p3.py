# ruff: noqa: F403, F405, E501
from .prefab_base import *  # noqa: F403

# fmt: off
from .prefab_p1 import load_prefab  # noqa: E402,E501
# fmt: on


def diff_prefabs(prefab_a_path: str, prefab_b_path: str) -> Dict[str, Any]:
    """Structural diff between two prefab files.

    Compares the RootObject summary plus the flat list of children (by Name)
    using the same logic as scene diff. Symmetric with scene.diff_scenes.

    Returns:
        Dict with 'root_changes' (or None if identical),
        'children_added' (list of names), 'children_removed' (list of names),
        'children_modified' (list of {name, changes}), and 'identical' (bool).
    """
    data_a = load_prefab(prefab_a_path)
    data_b = load_prefab(prefab_b_path)

    root_a = data_a.get("RootObject", {}) or {}
    root_b = data_b.get("RootObject", {}) or {}

    summary_root_a = scene_mod._object_summary(root_a)
    summary_root_b = scene_mod._object_summary(root_b)
    root_changes = scene_mod._diff_two_objects("<root>", summary_root_a, summary_root_b)

    children_a = scene_mod._flatten_objects(root_a.get("Children", []))
    children_b = scene_mod._flatten_objects(root_b.get("Children", []))
    summary_a = {
        obj.get("Name", f"<unnamed:{i}>"): scene_mod._object_summary(obj)
        for i, obj in enumerate(children_a)
    }
    summary_b = {
        obj.get("Name", f"<unnamed:{i}>"): scene_mod._object_summary(obj)
        for i, obj in enumerate(children_b)
    }

    names_a = set(summary_a.keys())
    names_b = set(summary_b.keys())
    added = sorted(names_b - names_a)
    removed = sorted(names_a - names_b)
    modified: List[Dict[str, Any]] = []
    for name in sorted(names_a & names_b):
        d = scene_mod._diff_two_objects(name, summary_a[name], summary_b[name])
        if d:
            modified.append(d)

    identical = (root_changes is None) and not (added or removed or modified)
    return {
        "prefab_a": prefab_a_path,
        "prefab_b": prefab_b_path,
        "root_changes": root_changes,
        "children_added": added,
        "children_removed": removed,
        "children_modified": modified,
        "identical": identical,
    }


def extract_asset_refs(prefab_path: str) -> Dict[str, List[str]]:
    """Extract every asset reference from a prefab file.

    Same categorization as scene.extract_asset_refs.
    """
    data = load_prefab(prefab_path)
    refs: Dict[str, List[str]] = {}
    if "RootObject" in data:
        scene_mod._walk_for_refs(data["RootObject"], refs, ["RootObject"])
    return {cat: sorted(set(paths)) for cat, paths in refs.items()}
