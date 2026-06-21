# ruff: noqa: F403, F405, E501
from .melt_backend_base import *  # noqa: F403

# fmt: off
from .melt_backend_p1 import _validate_codec, find_melt  # noqa: E402,E501
# fmt: on


def render_color_bars(
    output_path: str,
    duration: int = 3,
    width: int = 320,
    height: int = 240,
    fps: int = 25,
    vcodec: str = "libx264",
    acodec: str = "aac",
    overwrite: bool = False,
    timeout: int = 120,
) -> dict:
    """Render a color bars test video using melt's built-in producer.

    This doesn't require any input files — perfect for E2E testing.
    """
    _validate_codec(vcodec, ALLOWED_VCODECS, "video codec")
    _validate_codec(acodec, ALLOWED_ACODECS, "audio codec")

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}")

    melt = find_melt()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    frames = duration * fps
    cmd = [
        melt,
        f"color:red",
        f"out={fps - 1}",
        f"color:green",
        f"out={fps - 1}",
        f"color:blue",
        f"out={fps - 1}",
        "-consumer",
        f"avformat:{output_path}",
        f"width={width}",
        f"height={height}",
        f"frame_rate_num={fps}",
        f"vcodec={vcodec}",
        f"acodec={acodec}",
        "ar=48000",
        "channels=2",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"melt render failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr[-500:]}"
        )

    if not os.path.exists(output_path):
        raise RuntimeError(f"melt produced no output: {output_path}")

    return {
        "output": os.path.abspath(output_path),
        "format": os.path.splitext(output_path)[1].lstrip("."),
        "method": "melt",
        "file_size": os.path.getsize(output_path),
        "duration_seconds": duration,
    }
