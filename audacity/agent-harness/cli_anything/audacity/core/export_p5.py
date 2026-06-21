# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _human_size  # noqa: E402,E501
from .export_p2 import _render_track  # noqa: E402,E501
from .export_p4 import _apply_track_effects, _format_time  # noqa: E402,E501
# fmt: on


def render_mix(
    project: Dict[str, Any],
    output_path: str,
    preset: str = "wav",
    overwrite: bool = False,
    channels_override: Optional[int] = None,
) -> Dict[str, Any]:
    """Render the project: mix all tracks, apply effects, export.

    This is the main rendering pipeline.
    """
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file exists: {output_path}. Use --overwrite.")

    settings = project.get("settings", {})
    sample_rate = settings.get("sample_rate", 44100)
    bit_depth = settings.get("bit_depth", 16)
    out_channels = channels_override or settings.get("channels", 2)

    # Get preset settings
    if preset in EXPORT_PRESETS:
        p = EXPORT_PRESETS[preset]
        fmt = p["format"]
        if "bit_depth" in p["params"]:
            bit_depth = p["params"]["bit_depth"]
    else:
        raise ValueError(f"Unknown preset: {preset}")

    tracks = project.get("tracks", [])

    # Check for solo tracks
    solo_tracks = [t for t in tracks if t.get("solo", False)]
    has_solo = len(solo_tracks) > 0

    # Render each track
    rendered_tracks = []
    track_volumes = []
    track_pans = []

    for track in tracks:
        # Skip muted tracks; if solo mode is active, skip non-solo tracks
        if track.get("mute", False):
            continue
        if has_solo and not track.get("solo", False):
            continue

        track_audio = _render_track(track, sample_rate, out_channels)

        if track_audio:
            # Apply track-level effects
            track_audio = _apply_track_effects(
                track_audio,
                track.get("effects", []),
                sample_rate,
                out_channels,
            )
            rendered_tracks.append(track_audio)
            track_volumes.append(track.get("volume", 1.0))
            track_pans.append(track.get("pan", 0.0))

    # Mix all tracks together
    if rendered_tracks:
        mixed = mix_audio(
            rendered_tracks,
            volumes=track_volumes,
            pans=track_pans,
            channels=out_channels,
        )
    else:
        # Empty project: generate 1 second of silence
        mixed = generate_silence(1.0, sample_rate, out_channels)

    # Clamp to prevent clipping
    mixed = clamp_samples(mixed)

    # Export
    if fmt == "WAV":
        write_wav(output_path, mixed, sample_rate, out_channels, bit_depth)
    else:
        # For non-WAV formats, write a WAV first and note that conversion
        # requires external tools
        write_wav(output_path, mixed, sample_rate, out_channels, bit_depth)

    # Verify output
    file_size = os.path.getsize(output_path)
    duration = (len(mixed) / out_channels) / sample_rate

    result = {
        "output": os.path.abspath(output_path),
        "format": fmt,
        "sample_rate": sample_rate,
        "channels": out_channels,
        "bit_depth": bit_depth,
        "duration": round(duration, 3),
        "duration_human": _format_time(duration),
        "file_size": file_size,
        "file_size_human": _human_size(file_size),
        "preset": preset,
        "tracks_rendered": len(rendered_tracks),
        "peak_level": round(get_peak(mixed), 4),
        "rms_level": round(get_rms(mixed), 4),
    }

    return result
