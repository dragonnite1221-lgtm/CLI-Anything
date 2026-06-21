# ruff: noqa: F403, F405, E501
from .ffmpeg_backend_base import *  # noqa: F403

# fmt: off
from .ffmpeg_backend_p1 import find_ffmpeg  # noqa: E402,E501
# fmt: on


def render_segment(
    input_path: str,
    output_path: str,
    start_s: float,
    end_s: float,
    target_w: int,
    target_h: int,
    fps: int = 30,
    speed: float = 1.0,
    crop: Optional[dict] = None,
    overwrite: bool = True,
    timeout: int = 300,
) -> dict:
    """Render a video segment with optional crop and speed change.

    Args:
        input_path: Source video file.
        output_path: Destination MP4 file.
        start_s: Start time in seconds.
        end_s: End time in seconds.
        target_w: Output width.
        target_h: Output height.
        fps: Output frame rate.
        speed: Playback speed multiplier.
        crop: Optional dict with keys w, h, x, y (pixel values).
        overwrite: Whether to overwrite existing output.
        timeout: Subprocess timeout in seconds.

    Returns:
        Dict with output path, file_size, method.
    """
    exe = find_ffmpeg()
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output exists: {output_path}")

    vf_parts = []
    if crop:
        vf_parts.append(f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']}")
    vf_parts.append(f"scale={target_w}:{target_h}:flags=lanczos")
    if speed != 1.0:
        vf_parts.append(f"setpts={1.0 / speed}*PTS")

    af = None
    if speed != 1.0:
        af_parts = []
        s = speed
        while s > 2.0:
            af_parts.append("atempo=2.0")
            s /= 2.0
        while s < 0.5:
            af_parts.append("atempo=0.5")
            s *= 2.0
        af_parts.append(f"atempo={s:.4f}")
        af = ",".join(af_parts)

    cmd = [
        exe,
        "-y" if overwrite else "-n",
        "-ss",
        str(start_s),
        "-to",
        str(end_s),
        "-i",
        input_path,
        "-vf",
        ",".join(vf_parts),
    ]
    if af:
        cmd += ["-af", af]
    cmd += [
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-r",
        str(fps),
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg render failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr[-500:]}"
        )
    if not os.path.exists(output_path):
        raise RuntimeError(f"ffmpeg produced no output: {output_path}")

    return {
        "output": os.path.abspath(output_path),
        "file_size": os.path.getsize(output_path),
        "method": "ffmpeg",
    }


def concat_segments(
    segment_paths: list[str],
    output_path: str,
    overwrite: bool = True,
    timeout: int = 300,
) -> dict:
    """Concatenate multiple video segments into one file.

    Args:
        segment_paths: List of MP4 file paths to concatenate in order.
        output_path: Output MP4 path.

    Returns:
        Dict with output path, file_size, segment_count.
    """
    exe = find_ffmpeg()
    if not segment_paths:
        raise ValueError("No segments to concatenate")

    import tempfile

    concat_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    try:
        for sp in segment_paths:
            concat_file.write(f"file '{os.path.abspath(sp)}'\n")
        concat_file.close()

        cmd = [
            exe,
            "-y" if overwrite else "-n",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file.name,
            "-c",
            "copy",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {result.stderr[-500:]}")
    finally:
        os.unlink(concat_file.name)

    return {
        "output": os.path.abspath(output_path),
        "file_size": os.path.getsize(output_path),
        "segment_count": len(segment_paths),
        "method": "ffmpeg-concat",
    }
