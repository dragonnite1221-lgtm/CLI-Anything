# ruff: noqa: F403, F405, E501
from .media_base import *  # noqa: F403

# fmt: off
from .media_p1 import _find_tool  # noqa: E402,E501
# fmt: on


def generate_thumbnail(
    filepath: str,
    output: str,
    time: str = "00:00:01.000",
    width: int = 320,
    height: int = 180,
) -> dict:
    """Generate a thumbnail from a video file.

    Requires ffmpeg to be available.
    """
    filepath = os.path.abspath(filepath)
    output = os.path.abspath(output)

    ffmpeg = _find_tool("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for thumbnail generation")

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-ss",
            time,
            "-i",
            filepath,
            "-vframes",
            "1",
            "-s",
            f"{width}x{height}",
            output,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    return {
        "action": "generate_thumbnail",
        "source": filepath,
        "output": output,
        "time": time,
        "size": f"{width}x{height}",
    }
