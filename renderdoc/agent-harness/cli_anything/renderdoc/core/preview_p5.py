# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _attach_trajectory_ref  # noqa: E402,E501
# fmt: on


def latest(
    *,
    project_path: Optional[str] = None,
    recipe: Optional[str] = None,
    bundle_kind: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the latest preview bundle manifest for RenderDoc."""
    manifest = find_latest_manifest(
        software="renderdoc",
        recipe=recipe,
        bundle_kind=bundle_kind,
        project_path=project_path,
        root_dir=root_dir,
    )
    if manifest is None:
        raise FileNotFoundError("No RenderDoc preview bundle found")
    return _attach_trajectory_ref(manifest)
