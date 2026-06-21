# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


HARNESS_VERSION = "0.1.0"
RECIPES: Dict[str, Dict[str, Any]] = {
    "quick": {
        "description": "Capture thumbnail, output targets, and pipeline snapshot",
        "max_thumb_dim": 768,
    },
}
def list_recipes() -> List[Dict[str, Any]]:
    """Return available preview recipes."""
    recipes = [
        {
            "name": name,
            "description": config["description"],
            "bundle_kind": "capture",
            "artifacts": ["hero", "gallery", "metadata"],
        }
        for name, config in RECIPES.items()
    ]
    recipes.append(
        {
            "name": "diff",
            "description": "Compare two pipeline states and their output targets",
            "bundle_kind": "diff",
            "artifacts": ["gallery", "diff", "metadata"],
        }
    )
    return recipes
def _default_event_id(handle) -> Optional[int]:
    drawcalls = actions_mod.get_drawcalls_only(handle.controller)
    if not drawcalls:
        return None
    return int(drawcalls[-1]["eventId"])
def _compact_diff(obj: Any) -> Any:
    if isinstance(obj, dict):
        pruned = {}
        for key, value in obj.items():
            if value == "SAME":
                continue
            compacted = _compact_diff(value)
            if compacted is not None:
                pruned[key] = compacted
        return pruned or None
    if isinstance(obj, list):
        values = [_compact_diff(item) for item in obj if item != "SAME"]
        values = [item for item in values if item is not None]
        return values or None
    return obj
def _count_differences(obj: Any) -> int:
    if isinstance(obj, dict):
        return sum(_count_differences(value) for value in obj.values()) or len(obj)
    if isinstance(obj, list):
        return sum(_count_differences(item) for item in obj) or len(obj)
    return 1
def _trajectory_dir(capture_path: str, recipe: str, root_dir: Optional[str] = None) -> str:
    return str(
        bundle_root(
            "renderdoc",
            recipe,
            project_path=capture_path,
            root_dir=root_dir,
        ).resolve()
    )
def _attach_trajectory_ref(manifest: Dict[str, Any]) -> Dict[str, Any]:
    bundle_dir = manifest.get("_bundle_dir")
    context = manifest.get("context") or {}
    trajectory_ref = context.get("trajectory_path")
    if bundle_dir and trajectory_ref:
        trajectory_path = (Path(str(bundle_dir)) / str(trajectory_ref)).resolve()
        if trajectory_path.is_file():
            manifest["_trajectory_path"] = str(trajectory_path)
    return manifest
