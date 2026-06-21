# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403

# fmt: off
from .transitions_p2 import TRANSITION_REGISTRY  # noqa: E402,E501
# fmt: on


def add_transition(
    session: Session,
    transition_name: str,
    track_index: int,
    clip_a_index: int,
    duration_frames: int = 14,
    params: Optional[dict] = None,
) -> dict:
    """Add a transition between two adjacent clips on a track.

    Uses Shotcut's sub-tractor format so the transition is visible
    and editable in Shotcut's timeline UI.
    """
    session.checkpoint()
    fps_num, fps_den = _get_fps(session)
    playlist = _get_track_playlist(session, track_index)

    # Collect entry elements in playlist order, excluding existing transitions
    entries = [c for c in playlist if c.tag in ("entry", "blank")]
    clip_entries = [
        e
        for e in entries
        if e.tag == "entry" and not is_transition_entry(e, session.root)
    ]
    if clip_a_index < 0 or clip_a_index >= len(clip_entries) - 1:
        raise IndexError(
            f"Need two adjacent clips for transition; "
            f"clip_a_index {clip_a_index} out of range (0-{len(clip_entries) - 2})"
        )

    entry_a = clip_entries[clip_a_index]
    entry_b = clip_entries[clip_a_index + 1]

    # Verify no blanks or existing transitions between the two clips
    found_a = False
    for child in playlist:
        if child is entry_a:
            found_a = True
            continue
        if found_a:
            if child is entry_b:
                break
            if child.tag == "blank":
                raise ValueError(
                    f"Cannot add transition: blank gap between clip {clip_a_index} "
                    f"and {clip_a_index + 1}"
                )
            if child.tag == "entry" and is_transition_entry(child, session.root):
                raise ValueError(
                    f"Cannot add transition: a transition already exists "
                    f"between clip {clip_a_index} and {clip_a_index + 1}"
                )

    chain_a_id = entry_a.get("producer", "")
    chain_b_id = entry_b.get("producer", "")

    # Parse current in/out points
    src_a_in = parse_time_input(entry_a.get("in", "00:00:00.000"), fps_num, fps_den)
    src_a_out = parse_time_input(entry_a.get("out", "00:00:00.000"), fps_num, fps_den)
    src_b_in = parse_time_input(entry_b.get("in", "00:00:00.000"), fps_num, fps_den)
    src_b_out = parse_time_input(entry_b.get("out", "00:00:00.000"), fps_num, fps_den)

    dur_a = src_a_out - src_a_in
    dur_b = src_b_out - src_b_in

    trans_frames = min(duration_frames, dur_a, dur_b)
    if trans_frames <= 0:
        raise RuntimeError("Clips too short for transition")
    half_a = (trans_frames + 1) // 2
    half_b = trans_frames - half_a

    trans_tc = frames_to_timecode(trans_frames, fps_num, fps_den)

    new_src_a_out = src_a_out - half_a
    new_src_b_in = src_b_in + half_b

    new_src_a_out_tc = frames_to_timecode(new_src_a_out, fps_num, fps_den)
    new_src_b_in_tc = frames_to_timecode(new_src_b_in, fps_num, fps_den)

    # Track references inside the transition tractor must span the full
    # transition duration, not just half. Each track pulls from the
    # trimmed-off portion of its source clip.
    track_a_in = max(src_a_in, src_a_out - trans_frames)
    track_a_out = src_a_out
    track_b_in = src_b_in
    track_b_out = min(src_b_out, src_b_in + trans_frames)

    track_a_in_tc = frames_to_timecode(track_a_in, fps_num, fps_den)
    track_a_out_tc = frames_to_timecode(track_a_out, fps_num, fps_den)
    track_b_in_tc = frames_to_timecode(track_b_in, fps_num, fps_den)
    track_b_out_tc = frames_to_timecode(track_b_out, fps_num, fps_den)

    # Resolve transition service and params
    if transition_name in TRANSITION_REGISTRY:
        reg = TRANSITION_REGISTRY[transition_name]
        service = reg["service"]
        props = {}
        for pname, pinfo in reg["params"].items():
            props[pname] = pinfo["default"]
        if params:
            props.update(params)
    else:
        service = transition_name
        props = params or {}

    # Create sub-tractor (Shotcut format: has in/out, shotcut:transition property)
    trans_tractor = ET.Element("tractor")
    trans_id = mlt_xml.new_id("tractor")
    trans_tractor.set("id", trans_id)
    trans_tractor.set("in", "00:00:00.000")
    trans_tractor.set("out", trans_tc)
    mlt_xml.set_property(trans_tractor, "shotcut:transition", "lumaMix")

    tr_a = ET.SubElement(trans_tractor, "track")
    tr_a.set("producer", chain_a_id)
    tr_a.set("in", track_a_in_tc)
    tr_a.set("out", track_a_out_tc)

    tr_b = ET.SubElement(trans_tractor, "track")
    tr_b.set("producer", chain_b_id)
    tr_b.set("in", track_b_in_tc)
    tr_b.set("out", track_b_out_tc)

    # Luma (video) transition
    luma = ET.SubElement(trans_tractor, "transition")
    luma.set("id", mlt_xml.new_id("transition"))
    luma.set("out", trans_tc)
    mlt_xml.set_property(luma, "a_track", "0")
    mlt_xml.set_property(luma, "b_track", "1")
    mlt_xml.set_property(luma, "mlt_service", service)
    mlt_xml.set_property(luma, "factory", "loader")
    mlt_xml.set_property(luma, "progressive", "1")
    mlt_xml.set_property(luma, "alpha_over", "1")
    mlt_xml.set_property(luma, "fix_background_alpha", "1")
    mlt_xml.set_property(luma, "invert", "0")
    for k, v in props.items():
        mlt_xml.set_property(luma, k, str(v))

    # Mix (audio) transition — skip if the main service is already mix
    if service != "mix":
        mix = ET.SubElement(trans_tractor, "transition")
        mix.set("id", mlt_xml.new_id("transition"))
        mix.set("out", trans_tc)
        mlt_xml.set_property(mix, "a_track", "0")
        mlt_xml.set_property(mix, "b_track", "1")
        mlt_xml.set_property(mix, "start", "-1")
        mlt_xml.set_property(mix, "accepts_blanks", "1")
        mlt_xml.set_property(mix, "mlt_service", "mix")

    # Insert sub-tractor BEFORE the playlist that references it
    root = session.root
    for idx, child in enumerate(root):
        if child is playlist:
            root.insert(idx, trans_tractor)
            mlt_xml._register_tree(trans_tractor, root)
            break

    # Trim original entries so their trimmed-off portions feed the transition
    entry_a.set("out", new_src_a_out_tc)
    entry_b.set("in", new_src_b_in_tc)

    # Insert transition entry between the two clips in the playlist
    trans_entry = ET.Element("entry")
    trans_entry.set("producer", trans_id)
    trans_entry.set("in", "00:00:00.000")
    trans_entry.set("out", trans_tc)

    for i, child in enumerate(list(playlist)):
        if child is entry_a:
            playlist.insert(i + 1, trans_entry)
            break

    return {
        "action": "add_transition",
        "transition_name": transition_name,
        "service": service,
        "tractor_id": trans_id,
        "track_index": track_index,
        "clip_a_index": clip_a_index,
        "duration_frames": trans_frames,
        "params": props,
    }
