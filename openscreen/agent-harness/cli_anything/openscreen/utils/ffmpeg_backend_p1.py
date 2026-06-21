# ruff: noqa: F403, F405, E501
from .ffmpeg_backend_base import *  # noqa: F403


def find_ffmpeg() -> str:
    """Find the ffmpeg executable. Raises RuntimeError if not found."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    raise RuntimeError(
        "ffmpeg is not installed.\n"
        "  macOS:  brew install ffmpeg\n"
        "  Linux:  apt install ffmpeg\n"
        "  Windows: winget install ffmpeg"
    )


def find_ffprobe() -> str:
    """Find the ffprobe executable. Raises RuntimeError if not found."""
    path = shutil.which("ffprobe")
    if path:
        return path
    raise RuntimeError(
        "ffprobe is not installed (usually bundled with ffmpeg).\n"
        "  macOS:  brew install ffmpeg\n"
        "  Linux:  apt install ffmpeg"
    )


def probe(input_path: str) -> dict:
    """Probe a media file and return its metadata.

    Returns dict with keys: width, height, duration, fps, codec,
    has_audio, file_size, path.
    """
    exe = find_ffprobe()
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    cmd = [
        exe,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr[:500]}")

    data = json.loads(result.stdout)

    video_stream = None
    has_audio = False
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and video_stream is None:
            video_stream = s
        if s.get("codec_type") == "audio":
            has_audio = True

    if not video_stream:
        raise ValueError(f"No video stream in {input_path}")

    width = int(video_stream["width"])
    height = int(video_stream["height"])

    duration = float(data["format"].get("duration", 0))
    if duration == 0 and "duration" in video_stream:
        duration = float(video_stream["duration"])

    r_frame_rate = video_stream.get("r_frame_rate", "30/1")
    num, den = r_frame_rate.split("/")
    fps = float(num) / float(den) if float(den) != 0 else 30.0

    return {
        "width": width,
        "height": height,
        "duration": round(duration, 3),
        "fps": round(fps, 2),
        "codec": video_stream.get("codec_name", "unknown"),
        "has_audio": has_audio,
        "file_size": os.path.getsize(input_path),
        "path": os.path.abspath(input_path),
    }
