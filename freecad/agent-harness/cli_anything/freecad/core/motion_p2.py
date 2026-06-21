# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403

# fmt: off
from .motion_p1 import _next_id, _now_iso, _unique_name, _validate_motion_index  # noqa: E402,E501
# fmt: on


def _ensure_empty_dir(path: str, overwrite: bool) -> str:
    resolved = os.path.abspath(path)
    if os.path.isdir(resolved):
        if os.listdir(resolved):
            if not overwrite:
                raise FileExistsError(
                    f"Output directory already exists and is not empty: {resolved}. "
                    "Use overwrite=True to replace it."
                )
            shutil.rmtree(resolved)
    elif os.path.exists(resolved):
        raise FileExistsError(f"Output path exists and is not a directory: {resolved}")
    os.makedirs(resolved, exist_ok=True)
    return resolved


def _ffmpeg_path() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise RuntimeError(
        "ffmpeg is required for motion video export but was not found on PATH"
    )


def create_motion(
    project: Dict[str, Any],
    name: Optional[str] = None,
    *,
    duration: float = 2.0,
    fps: int = 24,
    camera: str = "hero",
    width: int = 1280,
    height: int = 960,
    background: str = "White",
    fit_mode: str = "initial",
) -> Dict[str, Any]:
    """Create a new motion sequence attached to the project."""
    items = ensure_collection(project, _COLLECTION_KEY)
    if float(duration) <= 0:
        raise ValueError("duration must be greater than 0")
    if int(fps) <= 0:
        raise ValueError("fps must be positive")
    if camera not in CAMERA_PRESETS:
        raise ValueError(
            f"Unknown camera '{camera}'. Valid: {', '.join(sorted(CAMERA_PRESETS))}"
        )
    if fit_mode not in FIT_MODES:
        raise ValueError(
            f"Unknown fit_mode '{fit_mode}'. Valid: {', '.join(sorted(FIT_MODES))}"
        )
    if int(width) <= 0 or int(height) <= 0:
        raise ValueError("width and height must be positive")

    motion = {
        "id": _next_id(project),
        "name": _unique_name(project, name or "Motion"),
        "duration": float(duration),
        "fps": int(fps),
        "camera": camera,
        "width": int(width),
        "height": int(height),
        "background": str(background),
        "fit_mode": fit_mode,
        "tracks": [],
        "metadata": {
            "created": _now_iso(),
            "modified": _now_iso(),
        },
    }
    items.append(motion)
    return motion


def list_motions(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return summary info for all motion sequences."""
    items = ensure_collection(project, _COLLECTION_KEY)
    result = []
    for index, motion in enumerate(items):
        keyframe_count = sum(
            len(track.get("keyframes", [])) for track in motion.get("tracks", [])
        )
        result.append(
            {
                "index": index,
                "id": motion.get("id"),
                "name": motion.get("name"),
                "duration": motion.get("duration"),
                "fps": motion.get("fps"),
                "camera": motion.get("camera"),
                "track_count": len(motion.get("tracks", [])),
                "keyframe_count": keyframe_count,
            }
        )
    return result


def get_motion(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return a single motion sequence."""
    return _validate_motion_index(project, index)


def delete_motion(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Delete and return a motion sequence."""
    items = ensure_collection(project, _COLLECTION_KEY)
    _validate_motion_index(project, index)
    return items.pop(index)
