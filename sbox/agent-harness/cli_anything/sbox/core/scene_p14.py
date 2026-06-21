# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403

# fmt: off
from .scene_p5 import load_scene  # noqa: E402,E501
from .scene_p13 import _walk_for_refs  # noqa: E402,E501
# fmt: on


def extract_asset_refs(scene_path: str) -> Dict[str, List[str]]:
    """Extract every asset reference from a scene file.

    Returns:
        Dict mapping category ("models", "materials", "sounds", "textures",
        "particles", "prefabs", "scenes", "animgraphs", "shaders", "other")
        to a sorted, deduplicated list of asset paths.
    """
    data = load_scene(scene_path)
    refs: Dict[str, List[str]] = {}
    _walk_for_refs(data.get("GameObjects", []), refs, ["GameObjects"])
    # Also walk SceneProperties (e.g. NavMesh references)
    if "SceneProperties" in data:
        _walk_for_refs(data["SceneProperties"], refs, ["SceneProperties"])
    # Deduplicate and sort each category
    return {cat: sorted(set(paths)) for cat, paths in refs.items()}


def _object_summary(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Compress a GameObject dict to its comparable surface for diffing."""
    comps_by_type: Dict[str, Dict[str, Any]] = {}
    for comp in obj.get("Components", []):
        ctype = comp.get("__type", "")
        if not ctype:
            continue
        # Strip internal keys, keep public properties
        stripped = {k: v for k, v in comp.items() if not k.startswith("__")}
        comps_by_type[ctype] = stripped

    return {
        "name": obj.get("Name", ""),
        "position": obj.get("Position", "0,0,0"),
        "rotation": obj.get("Rotation", "0,0,0,1"),
        "scale": obj.get("Scale", "1,1,1"),
        "tags": obj.get("Tags", ""),
        "enabled": obj.get("Enabled", True),
        "components": comps_by_type,
        "child_count": len(obj.get("Children", [])),
    }


def _diff_two_objects(
    name: str, a: Dict[str, Any], b: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Compare two object summaries and return the differences, or None if identical."""
    diffs: Dict[str, Any] = {}

    for field in ("position", "rotation", "scale", "tags", "enabled", "child_count"):
        if a.get(field) != b.get(field):
            diffs[field] = {"from": a.get(field), "to": b.get(field)}

    a_comps = a.get("components", {})
    b_comps = b.get("components", {})
    a_types = set(a_comps.keys())
    b_types = set(b_comps.keys())

    added_comps = sorted(b_types - a_types)
    removed_comps = sorted(a_types - b_types)
    modified_comps: Dict[str, Dict[str, Any]] = {}

    for ctype in a_types & b_types:
        if a_comps[ctype] != b_comps[ctype]:
            keys_a = set(a_comps[ctype].keys())
            keys_b = set(b_comps[ctype].keys())
            field_changes: Dict[str, Any] = {}
            for k in keys_a | keys_b:
                va, vb = a_comps[ctype].get(k), b_comps[ctype].get(k)
                if va != vb:
                    field_changes[k] = {"from": va, "to": vb}
            if field_changes:
                modified_comps[ctype] = field_changes

    if added_comps:
        diffs["components_added"] = added_comps
    if removed_comps:
        diffs["components_removed"] = removed_comps
    if modified_comps:
        diffs["components_modified"] = modified_comps

    if not diffs:
        return None
    return {"name": name, "changes": diffs}
