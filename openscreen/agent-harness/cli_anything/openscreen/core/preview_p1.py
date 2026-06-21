# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def list_recipes() -> List[Dict[str, Any]]:
    """Return available preview recipes."""
    return [
        {
            "name": name,
            "description": config["description"],
            "bundle_kind": "capture",
            "artifacts": ["preview-clip", "hero", "gallery"],
        }
        for name, config in RECIPES.items()
    ]


def _project_fingerprint(session: Session) -> str:
    if not session.is_open:
        raise RuntimeError("No project is open")
    media = session.data.get("media", {})
    source_video = media.get("screenVideoPath") or session.data.get("videoPath")
    payload: Dict[str, Any] = {
        "project_path": session.project_path,
        "session_id": session.session_id,
        "project_data": session.data,
    }
    if source_video and os.path.isfile(source_video):
        payload["source_video"] = {
            "path": os.path.abspath(source_video),
            "fingerprint": fingerprint_file(source_video),
        }
    return fingerprint_data(payload)


def _metrics(session: Session) -> Dict[str, Any]:
    editor = session.editor
    return {
        "zoom_region_count": len(editor.get("zoomRegions", [])),
        "speed_region_count": len(editor.get("speedRegions", [])),
        "trim_region_count": len(editor.get("trimRegions", [])),
        "annotation_count": len(editor.get("annotationRegions", [])),
        "aspect_ratio": editor.get("aspectRatio", "16:9"),
        "padding": editor.get("padding", 50),
        "background": editor.get("wallpaper", "gradient_dark"),
    }


def _trajectory_dir(
    session: Session, recipe: str, root_dir: Optional[str] = None
) -> str:
    return str(
        bundle_root(
            "openscreen",
            recipe,
            project_path=session.project_path,
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
