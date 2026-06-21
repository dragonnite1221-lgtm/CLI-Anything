# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403
# fmt: off
from .mlt_xml_p1 import _CLIP_KDENLIVE_ID_START, _SEQUENCE_FOLDER_ID, _SEQUENCE_KDENLIVE_ID, _add_disabled_filter, _add_prop, _compute_track_duration, frames_to_seconds, seconds_to_frames, seconds_to_timecode  # noqa: E402,E501
from .mlt_xml_p2 import _build_bin_clips, _build_track_tractors  # noqa: E402,E501
from .mlt_xml_p3 import _build_transitions  # noqa: E402,E501
# fmt: on


def build_mlt_xml(project: Dict[str, Any]) -> str:
    """Build a Kdenlive Gen 5 (doc version 1.1) compatible MLT XML document."""
    profile = project.get("profile", {})
    width = profile.get("width", 1920)
    height = profile.get("height", 1080)
    fps_num = profile.get("fps_num", 30)
    fps_den = profile.get("fps_den", 1)
    progressive = profile.get("progressive", True)
    dar_num = profile.get("dar_num", 16)
    dar_den = profile.get("dar_den", 9)

    sar_num = dar_num * height
    sar_den = dar_den * width

    bin_clips = project.get("bin", [])
    tracks = project.get("tracks", [])
    guides = project.get("guides", [])

    # Map clip IDs to numeric kdenlive IDs (4, 5, 6, ...)
    clip_kid = {}
    clip_data_by_id = {}
    for i, clip in enumerate(bin_clips):
        clip_kid[clip["id"]] = str(_CLIP_KDENLIVE_ID_START + i)
        clip_data_by_id[clip["id"]] = clip

    max_dur = 0
    track_durs = {}
    for track in tracks:
        td = _compute_track_duration(track, fps_num, fps_den)
        track_durs[track["id"]] = td
        max_dur = max(max_dur, td)
    if max_dur == 0:
        max_dur = seconds_to_frames(300, fps_num, fps_den)

    root = ET.Element("mlt")
    root.set("LC_NUMERIC", "C")
    root.set("version", "7.0.0")
    root.set("title", project.get("name", "untitled"))
    root.set("producer", "main_bin")

    ET.SubElement(root, "profile", {
        "description": profile.get("name", "custom"),
        "width": str(width),
        "height": str(height),
        "progressive": str(1 if progressive else 0),
        "sample_aspect_num": str(sar_num),
        "sample_aspect_den": str(sar_den),
        "display_aspect_num": str(dar_num),
        "display_aspect_den": str(dar_den),
        "frame_rate_num": str(fps_num),
        "frame_rate_den": str(fps_den),
        "colorspace": "709",
    })

    # Black track producer
    black = ET.SubElement(root, "producer", {"id": "producer0", "in": "0", "out": str(max_dur)})
    _add_prop(black, "resource", "black")
    _add_prop(black, "mlt_service", "color")
    _add_prop(black, "kdenlive:playlistid", "black_track")
    _add_prop(black, "set.test_audio", "0")

    # Sort tracks: audio first, video last so video appears on top in kdenlive
    audio_tracks = [t for t in tracks if t.get("type") == "audio"]
    video_tracks = [t for t in tracks if t.get("type") != "audio"]
    sorted_tracks = audio_tracks + video_tracks

    # Mapping: original track index in project["tracks"] -> sequence position
    orig_to_seq = {}
    for seq_idx, t in enumerate(sorted_tracks):
        orig_idx = tracks.index(t)
        orig_to_seq[orig_idx] = seq_idx

    # Per-track: chains, dual playlists, wrapping tractor
    chain_counter = 0
    filter_counter = 0
    transition_counter = 0
    track_tractor_ids = []

    chain_counter, filter_counter = _build_track_tractors(chain_counter, clip_data_by_id, clip_kid, filter_counter, fps_den, fps_num, root, sorted_tracks, track_durs, track_tractor_ids)

    # Sequence tractor (UUID id)
    doc_uuid = f"{{{uuid.uuid4()}}}"
    sequence_uuid = doc_uuid
    video_count = len(video_tracks)
    audio_count = len(audio_tracks)

    seq = ET.SubElement(root, "tractor", {"id": sequence_uuid, "in": "0", "out": str(max_dur)})
    _add_prop(seq, "kdenlive:uuid", sequence_uuid)
    _add_prop(seq, "kdenlive:clipname", "Sequence 1")
    _add_prop(seq, "kdenlive:sequenceproperties.hasAudio", "1" if audio_count > 0 else "0")
    _add_prop(seq, "kdenlive:sequenceproperties.hasVideo", "1" if video_count > 0 else "0")
    _add_prop(seq, "kdenlive:sequenceproperties.activeTrack", str(len(tracks) - 1 if tracks else 0))
    _add_prop(seq, "kdenlive:sequenceproperties.tracksCount", str(len(tracks)))
    _add_prop(seq, "kdenlive:sequenceproperties.documentuuid", sequence_uuid)
    dur_tc = seconds_to_timecode(frames_to_seconds(max_dur + 1, fps_num, fps_den)) if max_dur > 0 else "00:00:00.000"
    _add_prop(seq, "kdenlive:duration", dur_tc)
    _add_prop(seq, "kdenlive:maxduration", str(max_dur + 1))
    _add_prop(seq, "kdenlive:producer_type", "17")
    _add_prop(seq, "kdenlive:id", _SEQUENCE_KDENLIVE_ID)
    _add_prop(seq, "kdenlive:clip_type", "0")
    _add_prop(seq, "kdenlive:file_size", "0")
    _add_prop(seq, "kdenlive:folderid", _SEQUENCE_FOLDER_ID)
    _add_prop(seq, "kdenlive:sequenceproperties.videoTarget", str(len(sorted_tracks) - 1 if video_tracks else -1))
    _add_prop(seq, "kdenlive:sequenceproperties.audioTarget", str(audio_count - 1 if audio_count > 0 else -1))
    _add_prop(seq, "kdenlive:sequenceproperties.tracks", str(len(tracks)))
    _add_prop(seq, "kdenlive:sequenceproperties.zoom", "8")
    _add_prop(seq, "kdenlive:sequenceproperties.zonein", "0")
    _add_prop(seq, "kdenlive:sequenceproperties.zoneout", str(max_dur))
    _add_prop(seq, "kdenlive:sequenceproperties.groups", "[]")

    guides_data = [
        {"pos": seconds_to_frames(g["position"], fps_num, fps_den),
         "comment": g.get("label", ""),
         "type": g.get("type", "default")}
        for g in guides
    ]
    _add_prop(seq, "kdenlive:sequenceproperties.guides", json.dumps(guides_data))

    # Tracks: black track first, then per-track tractors
    ET.SubElement(seq, "track", {"producer": "producer0"})
    for tid in track_tractor_ids:
        ET.SubElement(seq, "track", {"producer": tid})

    # Internal mix transitions for audio tracks
    for i, track in enumerate(sorted_tracks):
        if track.get("type") == "audio":
            t = ET.SubElement(seq, "transition", {"id": f"transition{transition_counter}"})
            transition_counter += 1
            _add_prop(t, "a_track", "0")
            _add_prop(t, "b_track", str(i + 1))
            _add_prop(t, "mlt_service", "mix")
            _add_prop(t, "kdenlive_id", "mix")
            _add_prop(t, "internal_added", "237")
            _add_prop(t, "always_active", "1")
            _add_prop(t, "accepts_blanks", "1")
            _add_prop(t, "sum", "1")

    # Internal qtblend transitions for video tracks
    for i, track in enumerate(sorted_tracks):
        if track.get("type") != "audio":
            t = ET.SubElement(seq, "transition", {"id": f"transition{transition_counter}"})
            transition_counter += 1
            _add_prop(t, "a_track", "0")
            _add_prop(t, "b_track", str(i + 1))
            _add_prop(t, "mlt_service", "qtblend")
            _add_prop(t, "kdenlive_id", "qtblend")
            _add_prop(t, "internal_added", "237")
            _add_prop(t, "always_active", "1")
            _add_prop(t, "compositing", "0")
            _add_prop(t, "distort", "0")
            _add_prop(t, "rotate_center", "0")

    # User transitions
    _build_transitions(fps_den, fps_num, orig_to_seq, project, seq, tracks, transition_counter)

    # Sequence-level volume and panner filters
    filter_counter = _add_disabled_filter(seq, "volume", filter_counter)
    filter_counter = _add_disabled_filter(seq, "panner", filter_counter)

    # Bin clip chains (sequential numbering continues)
    bin_chain_ids = {}
    _build_bin_clips(bin_chain_ids, bin_clips, chain_counter, clip_kid, fps_den, fps_num, root)

    # Main bin playlist
    main_bin = ET.SubElement(root, "playlist", {"id": "main_bin"})
    _add_prop(main_bin, "kdenlive:folder.-1.2", "Sequences")
    _add_prop(main_bin, "kdenlive:sequenceFolder", _SEQUENCE_FOLDER_ID)
    _add_prop(main_bin, "kdenlive:docproperties.version", "1.1")
    _add_prop(main_bin, "kdenlive:docproperties.uuid", doc_uuid)
    _add_prop(main_bin, "kdenlive:docproperties.opensequences", sequence_uuid)
    _add_prop(main_bin, "kdenlive:docproperties.activetimeline", sequence_uuid)
    _add_prop(main_bin, "xml_retain", "1")

    ET.SubElement(main_bin, "entry", {"in": "0", "out": "0", "producer": sequence_uuid})
    for clip in bin_clips:
        dur = seconds_to_frames(clip.get("duration", 0), fps_num, fps_den)
        ET.SubElement(main_bin, "entry", {"in": "0", "out": str(max(dur - 1, 0)), "producer": bin_chain_ids[clip["id"]]})

    # Project tractor (last element — what melt plays)
    proj_tr = ET.SubElement(root, "tractor", {"id": "tractor_project", "in": "0", "out": str(max_dur)})
    _add_prop(proj_tr, "kdenlive:projectTractor", "1")
    ET.SubElement(proj_tr, "track", {"producer": sequence_uuid, "in": "0", "out": str(max_dur)})

    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")
