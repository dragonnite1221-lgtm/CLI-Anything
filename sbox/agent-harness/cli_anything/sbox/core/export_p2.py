# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _classify_asset, _parse_json_asset  # noqa: E402,E501
# fmt: on


def get_asset_info(asset_path: str) -> Dict[str, Any]:
    """Get detailed info about a specific asset file.

    For JSON-based assets (.scene, .prefab, .sound), parses the file and
    returns structure information (top-level keys, counts, etc.).

    Args:
        asset_path: Absolute or relative path to the asset file.

    Returns:
        Dict with asset metadata:
        - name: filename
        - path: absolute path
        - type: classified asset type
        - size_bytes: file size
        - exists: whether the file exists
        - json_info: (optional) structure info for JSON-based assets
    """
    abs_path = os.path.abspath(asset_path)
    filename = os.path.basename(abs_path)
    classified = _classify_asset(abs_path)

    info: Dict[str, Any] = {
        "name": filename,
        "path": abs_path,
        "type": classified,
        "exists": os.path.isfile(abs_path),
    }

    if not info["exists"]:
        info["size_bytes"] = 0
        return info

    try:
        info["size_bytes"] = os.path.getsize(abs_path)
    except OSError:
        info["size_bytes"] = 0

    # Attempt to parse JSON-based assets for structure info
    _, ext = os.path.splitext(filename)
    json_extensions = {".scene", ".prefab", ".sound"}
    if ext.lower() in json_extensions:
        info["json_info"] = _parse_json_asset(abs_path)

    return info


def _normalize_ref(ref: str) -> str:
    """Normalize a ref for comparison: lowercase, forward slashes, strip 'assets/' prefix."""
    if not ref:
        return ""
    n = ref.replace("\\", "/").strip().lower()
    if n.startswith("assets/"):
        n = n[len("assets/") :]
    return n


def _scan_project_refs(project_dir: str) -> Dict[str, List[Dict[str, str]]]:
    """Walk every scene/prefab in a project and return a map: ref -> [sources].

    Each source is a dict with 'file' (relative path) and 'category' (model/material/...).
    Returns the inverted index: normalized_ref -> list of {file, category, original_ref}.
    """
    from cli_anything.sbox.core import scene as scene_mod
    from cli_anything.sbox.core import prefab as prefab_mod

    assets_dir = os.path.join(project_dir, "Assets")
    if not os.path.isdir(assets_dir):
        return {}

    inverted: Dict[str, List[Dict[str, str]]] = {}

    for dirpath, _dirs, files in os.walk(assets_dir):
        for fname in files:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, project_dir).replace("\\", "/")
            ext = os.path.splitext(fname)[1].lower()

            try:
                if ext == ".scene":
                    refs = scene_mod.extract_asset_refs(full)
                elif ext == ".prefab":
                    refs = prefab_mod.extract_asset_refs(full)
                else:
                    continue
            except (OSError, json.JSONDecodeError, ValueError):
                continue

            for category, paths in refs.items():
                for ref in paths:
                    norm = _normalize_ref(ref)
                    inverted.setdefault(norm, []).append(
                        {
                            "file": rel,
                            "category": category,
                            "original_ref": ref,
                        }
                    )

    return inverted


def find_asset_refs(project_dir: str, asset_path: str) -> List[Dict[str, str]]:
    """Find every scene/prefab in a project that references *asset_path*.

    Args:
        project_dir: Root directory of the s&box project.
        asset_path: The asset path to look for (e.g. "models/dev/box.vmdl").
                    Matching is case-insensitive, slash-normalized, and the
                    "Assets/" prefix is optional.

    Returns:
        List of dicts with 'file' (referrer path), 'category' (asset category),
        and 'original_ref' (the exact string found in the file).  Empty list if
        no references are found.
    """
    inverted = _scan_project_refs(project_dir)
    target = _normalize_ref(asset_path)
    return inverted.get(target, [])
