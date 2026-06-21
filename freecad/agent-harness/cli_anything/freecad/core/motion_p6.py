# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403

# fmt: off
from .motion_p1 import _validate_motion_index  # noqa: E402,E501
from .motion_p2 import _ffmpeg_path  # noqa: E402,E501
from .motion_p5 import render_frames  # noqa: E402,E501
# fmt: on


def render_video(
    project: Dict[str, Any],
    motion_index: int,
    output_path: str,
    *,
    overwrite: bool = False,
    frames_dir: Optional[str] = None,
    keep_frames: bool = False,
    camera: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    background: Optional[str] = None,
    fit_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Render a motion sequence to PNG frames and encode an MP4/WebM/GIF video."""
    resolved_output_path = os.path.abspath(output_path)
    output_dirname = os.path.dirname(resolved_output_path) or "."
    os.makedirs(output_dirname, exist_ok=True)
    if os.path.exists(resolved_output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {resolved_output_path}. Use overwrite=True to replace it."
        )
    ext = Path(resolved_output_path).suffix.lower()
    if ext not in {".mp4", ".webm", ".gif"}:
        raise ValueError(
            "motion render-video currently supports .mp4, .webm, and .gif outputs"
        )

    temp_dir: Optional[str] = None
    if frames_dir:
        resolved_frames_dir = os.path.abspath(frames_dir)
    elif keep_frames:
        stem = Path(resolved_output_path).stem
        resolved_frames_dir = os.path.join(output_dirname, f"{stem}_frames")
    else:
        temp_dir = tempfile.mkdtemp(prefix="freecad_motion_frames_")
        resolved_frames_dir = temp_dir

    frame_result = render_frames(
        project,
        motion_index,
        resolved_frames_dir,
        overwrite=True,
        camera=camera,
        width=width,
        height=height,
        background=background,
        fit_mode=fit_mode,
    )
    motion = _validate_motion_index(project, motion_index)
    ffmpeg = _ffmpeg_path()

    input_pattern = os.path.join(frame_result["output_dir"], "frame_%05d.png")
    command = [ffmpeg, "-y", "-framerate", str(int(motion["fps"])), "-i", input_pattern]
    if ext == ".mp4":
        command.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", resolved_output_path])
    elif ext == ".webm":
        command.extend(
            ["-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p", resolved_output_path]
        )
    else:
        command.extend(
            [
                "-vf",
                "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                resolved_output_path,
            ]
        )

    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(resolved_output_path):
        raise RuntimeError(
            f"ffmpeg video encode failed (exit code {proc.returncode}): {proc.stderr.strip()}"
        )

    result = {
        "motion": motion["name"],
        "output": resolved_output_path,
        "format": ext.lstrip("."),
        "file_size": os.path.getsize(resolved_output_path),
        "frame_count": frame_result["frame_count"],
        "fps": motion["fps"],
        "frames_dir": frame_result["output_dir"],
        "sequence_path": frame_result["sequence_path"],
        "method": "freecad-gui-sequence+ffmpeg",
        "ffmpeg_command": command,
    }
    if temp_dir and not keep_frames:
        shutil.rmtree(temp_dir, ignore_errors=True)
        result["frames_dir"] = None
        result["sequence_path"] = None
    return result
