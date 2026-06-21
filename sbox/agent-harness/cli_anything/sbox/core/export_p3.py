# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import list_assets  # noqa: E402,E501
from .export_p2 import _normalize_ref, _scan_project_refs  # noqa: E402,E501
# fmt: on


def find_unused_assets(
    project_dir: str,
    asset_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Find assets in the project that aren't referenced by any scene/prefab.

    Note: only asset types whose references appear in scene/prefab JSON are
    detectable here (models, materials, sounds, textures, prefabs). Code,
    razor templates, and shaders are not analysed - they're excluded by
    default unless explicitly requested via *asset_types*.

    Args:
        project_dir: Root directory of the s&box project.
        asset_types: Optional list of asset types to consider (model, material,
                     sound, texture, prefab). Defaults to all referenceable types.

    Returns:
        List of dicts with 'path' (relative to Assets/), 'type', and 'size_bytes'.
    """
    referenceable = {"model", "material", "sound", "texture", "prefab"}
    if asset_types is None:
        wanted = referenceable
    else:
        wanted = set(asset_types) & referenceable

    inverted = _scan_project_refs(project_dir)
    referenced_norms = set(inverted.keys())

    all_assets = list_assets(project_dir, asset_type="all")
    unused: List[Dict[str, Any]] = []

    for asset in all_assets:
        if asset["type"] not in wanted:
            continue
        rel = asset["path"].replace("\\", "/")
        # Compare: both with and without the extension (some refs omit .vmdl)
        candidates = {_normalize_ref(rel)}
        stem, _ = os.path.splitext(rel)
        if stem:
            candidates.add(_normalize_ref(stem))
        if not (candidates & referenced_norms):
            unused.append(asset)

    return unused


def _rewrite_string_refs(
    node: Any,
    old_norm: str,
    old_stem_norm: str,
    new_path: str,
    new_stem: str,
    counter: List[int],
) -> None:
    """Recursively rewrite asset reference strings in a JSON tree.

    Mutates *node* in place. Matches both full-path refs (with extension) and
    stem-only refs (no extension). *counter* is a single-element mutable list
    used to track replacement count from inside the recursion.
    """
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, str) and value:
                norm = _normalize_ref(value)
                if norm == old_norm:
                    node[key] = new_path
                    counter[0] += 1
                elif norm == old_stem_norm and old_stem_norm:
                    node[key] = new_stem
                    counter[0] += 1
            else:
                _rewrite_string_refs(
                    value, old_norm, old_stem_norm, new_path, new_stem, counter
                )
    elif isinstance(node, list):
        for item in node:
            _rewrite_string_refs(
                item, old_norm, old_stem_norm, new_path, new_stem, counter
            )


def _rewrite_refs_in_project(
    project_dir: str,
    old_path: str,
    new_path: str,
) -> List[Dict[str, Any]]:
    """Rewrite every reference to *old_path* with *new_path* across all scenes/prefabs.

    Both arguments should be relative-to-Assets paths (e.g. "models/team/foo.vmdl").
    Returns a list of dicts {file, replacements} for each file actually modified.
    """
    from cli_anything.sbox.core import scene as scene_mod
    from cli_anything.sbox.core import prefab as prefab_mod

    assets_dir = os.path.join(project_dir, "Assets")
    old_norm = _normalize_ref(old_path)
    old_stem_norm, _ = os.path.splitext(old_norm)
    # Preserve the new path's case but use forward slashes
    new_path_normslash = new_path.replace("\\", "/")
    new_stem, _ = os.path.splitext(new_path_normslash)

    modified: List[Dict[str, Any]] = []

    for dirpath, _dirs, files in os.walk(assets_dir):
        for fname in files:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, project_dir).replace("\\", "/")
            ext = os.path.splitext(fname)[1].lower()
            if ext not in (".scene", ".prefab"):
                continue
            try:
                if ext == ".scene":
                    data = scene_mod.load_scene(full)
                else:
                    data = prefab_mod.load_prefab(full)
            except (OSError, json.JSONDecodeError, ValueError):
                continue

            counter = [0]
            _rewrite_string_refs(
                data, old_norm, old_stem_norm, new_path_normslash, new_stem, counter
            )
            if counter[0] > 0:
                if ext == ".scene":
                    scene_mod.save_scene(full, data)
                else:
                    prefab_mod.save_prefab(full, data)
                modified.append({"file": rel, "replacements": counter[0]})

    return modified
