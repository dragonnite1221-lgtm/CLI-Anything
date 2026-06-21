# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403

# fmt: off
from .motion_p1 import _validate_motion_index  # noqa: E402,E501
from .motion_p2 import _ensure_empty_dir  # noqa: E402,E501
from .motion_p3 import _motion_frames  # noqa: E402,E501
from .motion_p4 import _generate_motion_macro  # noqa: E402,E501
# fmt: on


def render_frames(
    project: Dict[str, Any],
    motion_index: int,
    output_dir: str,
    *,
    overwrite: bool = False,
    camera: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    background: Optional[str] = None,
    fit_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a motion sequence to a real frame directory via FreeCAD GUI capture."""
    motion = _validate_motion_index(project, motion_index)
    resolved_camera = camera or motion.get("camera", "hero")
    resolved_width = int(width or motion.get("width", 1280))
    resolved_height = int(height or motion.get("height", 960))
    resolved_background = str(background or motion.get("background", "White"))
    resolved_fit_mode = fit_mode or motion.get("fit_mode", "initial")
    if resolved_camera not in CAMERA_PRESETS:
        raise ValueError(f"Unknown camera '{resolved_camera}'")
    if resolved_fit_mode not in FIT_MODES:
        raise ValueError(f"Unknown fit_mode '{resolved_fit_mode}'")

    resolved_output_dir = _ensure_empty_dir(output_dir, overwrite=overwrite)
    frame_payload = _motion_frames(project, motion, resolved_output_dir)
    frames = frame_payload["frames"]
    if not frames:
        raise RuntimeError("Motion sequence produced no frames")

    macro = _generate_motion_macro(
        project,
        frames=frames,
        camera=resolved_camera,
        width=resolved_width,
        height=resolved_height,
        background=resolved_background,
        fit_mode=resolved_fit_mode,
    )
    result = freecad_backend.run_macro_content(
        macro,
        timeout=max(240, len(frames) * 8),
        gui_required=True,
        env={"QT_QPA_PLATFORM": "offscreen"},
    )
    if result["returncode"] != 0:
        raise RuntimeError(
            f"FreeCAD motion render failed (exit code {result['returncode']}): {result['stderr']}"
        )

    missing = [frame["path"] for frame in frames if not os.path.isfile(frame["path"])]
    if missing:
        raise RuntimeError(
            f"Motion render completed but {len(missing)} frame(s) are missing: {missing[:3]}"
        )

    sequence_path = os.path.join(resolved_output_dir, "sequence.json")
    sequence = {
        "motion_name": motion["name"],
        "motion_index": motion_index,
        "duration": motion["duration"],
        "fps": motion["fps"],
        "camera": resolved_camera,
        "width": resolved_width,
        "height": resolved_height,
        "background": resolved_background,
        "fit_mode": resolved_fit_mode,
        "frame_count": len(frames),
        "frames": [
            {
                "index": frame["index"],
                "time": frame["time"],
                "path": os.path.relpath(frame["path"], resolved_output_dir),
            }
            for frame in frames
        ],
        "unsupported_targets": frame_payload["unsupported_targets"],
        "method": "freecad-gui-sequence",
    }
    with open(sequence_path, "w", encoding="utf-8") as fh:
        json.dump(sequence, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    return {
        "motion": motion["name"],
        "output_dir": resolved_output_dir,
        "sequence_path": sequence_path,
        "frame_count": len(frames),
        "first_frame": frames[0]["path"],
        "last_frame": frames[-1]["path"],
        "camera": resolved_camera,
        "fit_mode": resolved_fit_mode,
        "method": "freecad-gui-sequence",
        "unsupported_targets": frame_payload["unsupported_targets"],
    }
