# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def latest(
    *,
    project_path: Optional[str] = None,
    recipe: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the latest preview bundle manifest for Blender."""
    manifest = find_latest_manifest(
        software="blender",
        recipe=recipe,
        bundle_kind="capture",
        project_path=project_path,
        root_dir=root_dir,
    )
    if manifest is None:
        raise FileNotFoundError("No Blender preview bundle found")
    return manifest
