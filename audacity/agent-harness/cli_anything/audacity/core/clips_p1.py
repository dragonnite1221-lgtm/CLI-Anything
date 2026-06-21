# ruff: noqa: F403, F405, E501
from .clips_base import *  # noqa: F403


def struct_error():
    """Return struct.error for exception handling."""
    import struct

    return struct.error


def _guess_format(path: str) -> str:
    """Guess audio format from extension."""
    ext = os.path.splitext(path)[1].lower()
    fmt_map = {
        ".wav": "WAV",
        ".mp3": "MP3",
        ".flac": "FLAC",
        ".ogg": "OGG",
        ".aiff": "AIFF",
        ".aif": "AIFF",
        ".m4a": "M4A",
        ".wma": "WMA",
    }
    return fmt_map.get(ext, "unknown")


def import_audio(path: str) -> Dict[str, Any]:
    """Probe an audio file and return clip-ready metadata."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")

    abs_path = os.path.abspath(path)
    info = {
        "source": abs_path,
        "filename": os.path.basename(path),
        "file_size": os.path.getsize(abs_path),
    }

    # Try to read WAV info
    try:
        with wave.open(abs_path, "r") as wf:
            info["sample_rate"] = wf.getframerate()
            info["channels"] = wf.getnchannels()
            info["bit_depth"] = wf.getsampwidth() * 8
            info["frames"] = wf.getnframes()
            info["duration"] = wf.getnframes() / wf.getframerate()
            info["format"] = "WAV"
    except (wave.Error, EOFError, struct_error()):
        # Not a WAV or unreadable — store basic info
        info["duration"] = 0.0
        info["format"] = _guess_format(abs_path)

    return info


def add_clip(
    project: Dict[str, Any],
    track_index: int,
    source: str,
    name: Optional[str] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    trim_start: float = 0.0,
    trim_end: Optional[float] = None,
    volume: float = 1.0,
) -> Dict[str, Any]:
    """Add a clip to a track."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(
            f"Track index {track_index} out of range (0-{len(tracks) - 1})"
        )

    track = tracks[track_index]
    clips = track.setdefault("clips", [])

    abs_source = os.path.abspath(source) if source else ""

    # Determine duration from source if available
    duration = 0.0
    if abs_source and os.path.exists(abs_source):
        try:
            with wave.open(abs_source, "r") as wf:
                duration = wf.getnframes() / wf.getframerate()
        except (wave.Error, EOFError):
            pass

    if end_time is None:
        end_time = start_time + (duration - trim_start if duration > 0 else 10.0)
    if trim_end is None:
        trim_end = duration if duration > 0 else (end_time - start_time + trim_start)

    if start_time < 0:
        raise ValueError(f"start_time must be >= 0, got {start_time}")
    if end_time < start_time:
        raise ValueError(f"end_time ({end_time}) must be >= start_time ({start_time})")

    # Generate unique clip ID
    existing_ids = {c.get("id", i) for i, c in enumerate(clips)}
    new_id = 0
    while new_id in existing_ids:
        new_id += 1

    if name is None:
        name = (
            os.path.splitext(os.path.basename(source))[0]
            if source
            else f"clip_{new_id}"
        )

    clip = {
        "id": new_id,
        "name": name,
        "source": abs_source,
        "start_time": start_time,
        "end_time": end_time,
        "trim_start": trim_start,
        "trim_end": trim_end,
        "volume": volume,
    }
    clips.append(clip)
    return clip
