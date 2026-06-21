# ruff: noqa: F403, F405, E501
from .ffmpeg_backend_base import *  # noqa: F403

# fmt: off
from .ffmpeg_backend_p1 import find_ffmpeg  # noqa: E402,E501
# fmt: on


def composite_on_background(
    input_path: str,
    output_path: str,
    canvas_w: int,
    canvas_h: int,
    video_w: int,
    video_h: int,
    bg_color: str = "#1a1a2e",
    fps: int = 30,
    overwrite: bool = True,
    timeout: int = 300,
) -> dict:
    """Composite a video centered on a solid-color background.

    Args:
        input_path: Source video (already scaled to video_w x video_h).
        output_path: Output MP4 path.
        canvas_w, canvas_h: Full output canvas size.
        video_w, video_h: Video size within canvas.
        bg_color: Hex color for background.
        fps: Output frame rate.
    """
    exe = find_ffmpeg()
    x_off = (canvas_w - video_w) // 2
    y_off = (canvas_h - video_h) // 2

    cmd = [
        exe,
        "-y" if overwrite else "-n",
        "-f",
        "lavfi",
        "-i",
        f"color=c='{bg_color}':s={canvas_w}x{canvas_h}:r={fps}",
        "-i",
        input_path,
        "-filter_complex",
        f"[1:v]scale={video_w}:{video_h}[fg];"
        f"[0:v][fg]overlay={x_off}:{y_off}:shortest=1",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-map",
        "1:a?",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg composite failed: {result.stderr[-500:]}")

    return {
        "output": os.path.abspath(output_path),
        "file_size": os.path.getsize(output_path),
        "method": "ffmpeg-composite",
    }


def extract_frames(
    input_path: str,
    output_dir: str,
    fps: float = 2.0,
    max_frames: int = 60,
    scale_width: int = 960,
) -> list[str]:
    """Extract frames from a video for analysis.

    Returns list of JPEG file paths.
    """
    exe = find_ffmpeg()
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        exe,
        "-y",
        "-i",
        input_path,
        "-vf",
        f"fps={fps},scale={scale_width}:-1",
        "-frames:v",
        str(max_frames),
        "-q:v",
        "3",
        os.path.join(output_dir, "frame_%04d.jpg"),
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=120)

    return sorted(
        [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith("frame_") and f.endswith(".jpg")
        ]
    )
