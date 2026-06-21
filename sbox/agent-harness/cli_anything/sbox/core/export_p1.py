# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _classify_asset(file_path: str) -> str:
    """Classify an asset file by its extension.

    Returns the asset type string (e.g. 'scene', 'model') or 'other'.
    """
    _, ext = os.path.splitext(file_path)
    return _EXT_TO_TYPE.get(ext.lower(), "other")


def _get_extensions_for_type(asset_type: str) -> Optional[List[str]]:
    """Return the list of extensions for a given asset type, or None if 'all'."""
    if asset_type == "all":
        return None
    return ASSET_EXTENSIONS.get(asset_type)


def list_assets(
    project_dir: str,
    asset_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List all assets in a project's Assets/ directory.

    Args:
        project_dir: Root directory of the s&box project.
        asset_type: Filter by type - 'scene', 'prefab', 'material', 'model',
                    'sound', 'texture', 'shader', 'razor', 'code', or 'all'.
                    If None or 'all', returns every recognised asset.

    Returns:
        List of dicts, each with keys: path, type, name, size_bytes.
        Paths are relative to the project's Assets/ directory.
    """
    assets_dir = os.path.join(project_dir, "Assets")
    if not os.path.isdir(assets_dir):
        return []

    filter_type = asset_type or "all"
    allowed_extensions = _get_extensions_for_type(filter_type)

    results: List[Dict[str, Any]] = []

    for dirpath, _dirnames, filenames in os.walk(assets_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            _, ext = os.path.splitext(filename)
            ext_lower = ext.lower()

            # If filtering by type, skip files that don't match
            if allowed_extensions is not None and ext_lower not in allowed_extensions:
                continue

            # If showing all, skip files that aren't a recognised asset type
            classified = _EXT_TO_TYPE.get(ext_lower)
            if allowed_extensions is None and classified is None:
                continue

            rel_path = os.path.relpath(full_path, assets_dir)

            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0

            results.append(
                {
                    "path": rel_path,
                    "type": classified or "other",
                    "name": filename,
                    "size_bytes": size,
                }
            )

    # Sort by relative path for stable ordering
    results.sort(key=lambda entry: entry["path"])
    return results


def _parse_json_asset(file_path: str) -> Dict[str, Any]:
    """Parse a JSON asset file and return structure information.

    Returns a dict with:
    - top_level_keys: list of keys in the root object
    - For .scene files: game_object_count, scene_properties
    - For .prefab files: game_object_count
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {"error": f"Failed to parse JSON: {exc}"}

    if not isinstance(data, dict):
        return {"top_level_keys": [], "note": "Root element is not an object"}

    result: Dict[str, Any] = {
        "top_level_keys": list(data.keys()),
    }

    # Scene-specific info
    game_objects = data.get("GameObjects")
    if isinstance(game_objects, list):
        result["game_object_count"] = len(game_objects)
        result["game_object_names"] = [
            obj.get("Name", "<unnamed>")
            for obj in game_objects
            if isinstance(obj, dict)
        ]

    scene_props = data.get("SceneProperties")
    if isinstance(scene_props, dict):
        result["scene_properties"] = scene_props

    # Version info if present
    if "__version" in data:
        result["version"] = data["__version"]

    return result
