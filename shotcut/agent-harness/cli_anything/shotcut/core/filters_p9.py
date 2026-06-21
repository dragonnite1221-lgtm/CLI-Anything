# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p8 import FILTER_REGISTRY  # noqa: E402,E501
# fmt: on


def _resolve_target(
    session: Session,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
) -> ET.Element:
    """Resolve the target element for a filter (clip producer or track playlist)."""
    if track_index is None:
        # Apply to the main tractor (global filter)
        return session.get_main_tractor()

    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    producer_id = tracks[track_index].get("producer")
    playlist = mlt_xml.find_element_by_id(session.root, producer_id)
    if playlist is None:
        raise RuntimeError(f"Track playlist not found")

    if clip_index is None:
        # Apply to the track
        return playlist

    # Apply to a specific clip's producer
    clip_entries = real_clip_entries(
        mlt_xml.get_playlist_entries(playlist), session.root
    )
    if clip_index < 0 or clip_index >= len(clip_entries):
        raise IndexError(f"Clip index {clip_index} out of range")

    clip_producer_id = clip_entries[clip_index]["producer"]
    producer = mlt_xml.find_element_by_id(session.root, clip_producer_id)
    if producer is None:
        raise RuntimeError(f"Producer {clip_producer_id!r} not found")
    return producer


def add_filter(
    session: Session,
    filter_name: str,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
    params: Optional[dict] = None,
) -> dict:
    """Add a filter to a clip, track, or the whole timeline.

    Args:
        session: Active session
        filter_name: Name from FILTER_REGISTRY, or raw MLT service name
        track_index: Track index (None = global)
        clip_index: Clip index on the track (None = whole track)
        params: Parameter overrides (name → value)
    """
    session.checkpoint()

    # Look up in registry, or use as raw service name
    if filter_name in FILTER_REGISTRY:
        reg = FILTER_REGISTRY[filter_name]
        service = reg["service"]
        # Start with defaults
        props = {}
        for pname, pinfo in reg["params"].items():
            props[pname] = pinfo["default"]
        # Apply overrides
        if params:
            props.update(params)
    else:
        # Assume it's a raw MLT service name
        service = filter_name
        props = params or {}

    target = _resolve_target(session, track_index, clip_index)
    shotcut_filter_name = filter_name if filter_name in FILTER_REGISTRY else None
    filt = mlt_xml.add_filter_to_element(target, service, shotcut_filter_name, props)

    target_desc = "global"
    if track_index is not None and clip_index is not None:
        target_desc = f"track {track_index}, clip {clip_index}"
    elif track_index is not None:
        target_desc = f"track {track_index}"

    return {
        "action": "add_filter",
        "filter_name": filter_name,
        "service": service,
        "filter_id": filt.get("id"),
        "target": target_desc,
        "params": props,
    }
