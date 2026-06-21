# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p2 import find_asset_refs  # noqa: E402,E501
from .export_p3 import _rewrite_refs_in_project  # noqa: E402,E501
# fmt: on


def rename_asset(
    project_dir: str,
    old_path: str,
    new_name: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Rename an asset file and update every scene/prefab reference.

    Args:
        project_dir: Project root directory.
        old_path: Current asset path (relative to Assets/, e.g. "models/team/foo.vmdl").
        new_name: New filename (no path), keeping the same parent directory.
                  Extension may be omitted - the existing extension is preserved.
        dry_run: If True, don't touch any files - just report what would change.

    Returns:
        Dict with old_path, new_path, file_renamed, references_updated (list).
    """
    assets_dir = os.path.join(project_dir, "Assets")
    old_full = os.path.join(assets_dir, old_path.replace("/", os.sep))
    if not os.path.isfile(old_full):
        raise FileNotFoundError(f"Asset not found: {old_path}")

    parent_rel = os.path.dirname(old_path.replace("\\", "/"))
    old_ext = os.path.splitext(old_path)[1]
    # Preserve extension if caller omitted it
    if not os.path.splitext(new_name)[1]:
        new_filename = new_name + old_ext
    else:
        new_filename = new_name

    new_path = (parent_rel + "/" + new_filename).lstrip("/")
    new_full = os.path.join(assets_dir, new_path.replace("/", os.sep))

    if os.path.exists(new_full) and os.path.abspath(new_full) != os.path.abspath(
        old_full
    ):
        raise FileExistsError(f"Target already exists: {new_path}")

    if dry_run:
        # Count refs without writing
        refs = find_asset_refs(project_dir, old_path)
        return {
            "old_path": old_path,
            "new_path": new_path,
            "file_renamed": False,
            "references_updated": [],
            "references_would_update": len(refs),
            "dry_run": True,
        }

    updated = _rewrite_refs_in_project(project_dir, old_path, new_path)
    os.rename(old_full, new_full)

    return {
        "old_path": old_path,
        "new_path": new_path,
        "file_renamed": True,
        "references_updated": updated,
        "dry_run": False,
    }


def move_asset(
    project_dir: str,
    old_path: str,
    new_path: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Move an asset to a new path (potentially different directory) and update refs.

    Args:
        project_dir: Project root directory.
        old_path: Current asset path relative to Assets/.
        new_path: Target path relative to Assets/. May change directory and/or filename.
                  Extension is preserved if the caller's new_path lacks one.
        dry_run: If True, don't touch any files - just report what would change.

    Returns:
        Dict with old_path, new_path, file_moved, references_updated (list).
    """
    assets_dir = os.path.join(project_dir, "Assets")
    old_full = os.path.join(assets_dir, old_path.replace("/", os.sep))
    if not os.path.isfile(old_full):
        raise FileNotFoundError(f"Asset not found: {old_path}")

    old_ext = os.path.splitext(old_path)[1]
    new_path_norm = new_path.replace("\\", "/")
    if not os.path.splitext(new_path_norm)[1]:
        new_path_norm = new_path_norm + old_ext

    new_full = os.path.join(assets_dir, new_path_norm.replace("/", os.sep))

    if os.path.exists(new_full) and os.path.abspath(new_full) != os.path.abspath(
        old_full
    ):
        raise FileExistsError(f"Target already exists: {new_path_norm}")

    if dry_run:
        refs = find_asset_refs(project_dir, old_path)
        return {
            "old_path": old_path,
            "new_path": new_path_norm,
            "file_moved": False,
            "references_updated": [],
            "references_would_update": len(refs),
            "dry_run": True,
        }

    updated = _rewrite_refs_in_project(project_dir, old_path, new_path_norm)
    os.makedirs(os.path.dirname(new_full) or assets_dir, exist_ok=True)
    os.rename(old_full, new_full)

    return {
        "old_path": old_path,
        "new_path": new_path_norm,
        "file_moved": True,
        "references_updated": updated,
        "dry_run": False,
    }


def find_project_dir(start_path: str) -> Optional[str]:
    """Walk up from start_path to find the directory containing a .sbproj file.

    Starts from start_path (or its parent if start_path is a file) and
    checks each ancestor directory for a .sbproj file.

    Args:
        start_path: File or directory path to start searching from.

    Returns:
        The project directory path (containing the .sbproj), or None if
        no .sbproj file is found before reaching the filesystem root.
    """
    current = os.path.abspath(start_path)

    # If start_path is a file, begin from its parent directory
    if os.path.isfile(current):
        current = os.path.dirname(current)

    while True:
        # Check for any .sbproj file in this directory
        try:
            entries = os.listdir(current)
        except OSError:
            return None

        for entry in entries:
            if entry.endswith(".sbproj"):
                return current

        # Move to parent
        parent = os.path.dirname(current)
        if parent == current:
            # Reached filesystem root
            return None
        current = parent
