# ruff: noqa: F403, F405, E501
from .compositing_base import *  # noqa: F403


def pip_position(
    session: Session,
    track_index: int,
    clip_index: int,
    x: str = "0",
    y: str = "0",
    width: str = "100%",
    height: str = "100%",
    opacity: float = 1.0,
) -> dict:
    """Set picture-in-picture position and size for a clip.

    This applies/updates an affine filter on the clip to position it
    as a picture-in-picture overlay.

    Args:
        session: Active session
        track_index: Track containing the clip
        clip_index: Clip index on the track
        x: X position (pixels or percentage like "10%" or "100")
        y: Y position (pixels or percentage)
        width: Width (pixels or percentage)
        height: Height (pixels or percentage)
        opacity: Opacity (0.0-1.0)
    """
    session.checkpoint()

    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)

    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    producer_id = tracks[track_index].get("producer")
    playlist = mlt_xml.find_element_by_id(session.root, producer_id)
    if playlist is None:
        raise RuntimeError("Track playlist not found")

    clip_entries = real_clip_entries(
        mlt_xml.get_playlist_entries(playlist), session.root
    )
    if clip_index < 0 or clip_index >= len(clip_entries):
        raise IndexError(f"Clip index {clip_index} out of range")

    clip_producer_id = clip_entries[clip_index]["producer"]
    producer = mlt_xml.find_element_by_id(session.root, clip_producer_id)
    if producer is None:
        raise RuntimeError(f"Producer {clip_producer_id!r} not found")

    # Build geometry string: x/y:wxh:opacity
    opacity_int = int(opacity * 100)
    geometry = f"{x}/{y}:{width}x{height}:{opacity_int}"

    # Look for existing affine filter, or create one
    for filt in producer.findall("filter"):
        svc = mlt_xml.get_property(filt, "mlt_service", "")
        if svc == "affine":
            mlt_xml.set_property(filt, "transition.geometry", geometry)
            return {
                "action": "pip_position",
                "track_index": track_index,
                "clip_index": clip_index,
                "geometry": geometry,
            }

    # Create new affine filter
    mlt_xml.add_filter_to_element(
        producer,
        "affine",
        shotcut_filter="affine",
        properties={"transition.geometry": geometry, "background": "color:#00000000"},
    )

    return {
        "action": "pip_position",
        "track_index": track_index,
        "clip_index": clip_index,
        "geometry": geometry,
    }
