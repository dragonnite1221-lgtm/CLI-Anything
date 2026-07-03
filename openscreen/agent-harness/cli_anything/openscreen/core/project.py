"""Project operations — new, open, save, info, set video source."""

import os
from typing import Optional

from .session import Session
from ..utils import ffmpeg_backend
# Re-exported for backward compatibility (moved to settings.py).
from .settings import (  # noqa: F401
    ASPECT_RATIOS,
    BACKGROUNDS,
    EXPORT_QUALITIES,
    EXPORT_FORMATS,
    _validate_crop_region,
    set_setting,
)


def new_project(session: Session, video_path: Optional[str] = None) -> dict:
    """Create a new Openscreen project.

    Args:
        session: The active session.
        video_path: Optional path to a screen recording to attach.

    Returns:
        Project info dict.
    """
    session.new_project(video_path)
    result = {"status": "created", "video": None}
    if video_path:
        result["video"] = os.path.abspath(video_path)
    return result


def open_project(session: Session, path: str) -> dict:
    """Open an existing .openscreen project file.

    Returns:
        Project info dict.
    """
    session.open_project(path)
    return info(session)


def save_project(session: Session, path: Optional[str] = None) -> dict:
    """Save the current project.

    Returns:
        Dict with saved path.
    """
    saved = session.save_project(path)
    return {"status": "saved", "path": saved}


def info(session: Session) -> dict:
    """Get project information.

    Returns:
        Dict with project metadata and editor state summary.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    editor = session.editor
    media = session.data.get("media", {})

    return {
        "version": session.data.get("version", 1),
        "project_path": session.project_path,
        "modified": session.is_modified,
        "video": media.get("screenVideoPath"),
        "webcam_video": media.get("webcamVideoPath"),
        "aspect_ratio": editor.get("aspectRatio", "16:9"),
        "background": editor.get("wallpaper", "gradient_dark"),
        "padding": editor.get("padding", 50),
        "border_radius": editor.get("borderRadius", 12),
        "shadow_intensity": editor.get("shadowIntensity", 0),
        "motion_blur": editor.get("motionBlurAmount", 0),
        "export_quality": editor.get("exportQuality", "good"),
        "export_format": editor.get("exportFormat", "mp4"),
        "zoom_regions": len(editor.get("zoomRegions", [])),
        "speed_regions": len(editor.get("speedRegions", [])),
        "trim_regions": len(editor.get("trimRegions", [])),
        "annotations": len(editor.get("annotationRegions", [])),
    }


def set_video(session: Session, video_path: str) -> dict:
    """Set the source video for the project."""
    if not session.is_open:
        raise RuntimeError("No project is open")

    path = os.path.abspath(video_path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Video file not found: {path}")

    session.checkpoint()
    if "media" not in session.data:
        session.data["media"] = {}
    session.data["media"]["screenVideoPath"] = path
    return {"status": "ok", "video": path}
