# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403
# fmt: off
from .mlt_xml_p1 import _add_disabled_filter, _add_prop, _clip_type_num, _set_producer_props, seconds_to_frames  # noqa: E402,E501
# fmt: on


def _build_track_tractors(chain_counter, clip_data_by_id, clip_kid, filter_counter, fps_den, fps_num, root, sorted_tracks, track_durs, track_tractor_ids):
    for track in sorted_tracks:
        track_type = track.get("type", "video")
        is_audio = track_type == "audio"
        tractor_id = f"tractor{track['id']}"

        # Chain per unique clip in this track
        track_clip_chains = {}
        for clip_entry in track.get("clips", []):
            clip_id = clip_entry.get("clip_id", "")
            if clip_id in track_clip_chains:
                continue
            chain_id = f"chain{chain_counter}"
            chain_counter += 1
            clip_data = clip_data_by_id.get(clip_id)
            if not clip_data:
                track_clip_chains[clip_id] = clip_id
                continue
            dur = seconds_to_frames(clip_data.get("duration", 0), fps_num, fps_den)
            chain = ET.SubElement(root, "chain", {"id": chain_id, "in": "0", "out": str(max(dur - 1, 0))})
            _add_prop(chain, "length", str(dur))
            _add_prop(chain, "eof", "pause")
            _add_prop(chain, "resource", clip_data.get("source", ""))
            _set_producer_props(chain, clip_data.get("type", "video"))
            _add_prop(chain, "kdenlive:folderid", "-1")
            _add_prop(chain, "kdenlive:id", clip_kid.get(clip_id, clip_id))
            _add_prop(chain, "mute_on_pause", "0")
            _add_prop(chain, "kdenlive:clip_type", str(_clip_type_num(clip_data.get("type", "video"))))
            if is_audio:
                _add_prop(chain, "set.test_audio", "0")
                _add_prop(chain, "set.test_image", "1")
            else:
                _add_prop(chain, "set.test_audio", "1")
                _add_prop(chain, "set.test_image", "0")
            track_clip_chains[clip_id] = chain_id

        # Playlist 1: clip entries
        pl1 = ET.SubElement(root, "playlist", {"id": f"playlist{track['id'] * 2}"})
        if is_audio:
            _add_prop(pl1, "kdenlive:audio_track", "1")

        prev_end = 0.0
        for clip_entry in track.get("clips", []):
            cid = clip_entry.get("clip_id", "")
            if cid not in clip_data_by_id:
                continue
            pos = clip_entry.get("position", 0.0)
            gap = pos - prev_end
            if gap > 0.001:
                ET.SubElement(pl1, "blank", {"length": str(seconds_to_frames(gap, fps_num, fps_den))})

            in_f = seconds_to_frames(clip_entry.get("in", 0), fps_num, fps_den)
            out_f = seconds_to_frames(clip_entry.get("out", 0), fps_num, fps_den)
            ref = track_clip_chains.get(cid, cid)
            entry = ET.SubElement(pl1, "entry", {"producer": ref, "in": str(in_f), "out": str(max(out_f - 1, 0))})

            for filt in clip_entry.get("filters", []):
                f_el = ET.SubElement(entry, "filter", {"id": f"filter{filter_counter}"})
                filter_counter += 1
                _add_prop(f_el, "mlt_service", filt.get("mlt_service", ""))
                kdenlive_id = FILTER_REGISTRY.get(filt.get("name", ""), {}).get("kdenlive_name", filt.get("mlt_service", ""))
                _add_prop(f_el, "kdenlive_id", kdenlive_id)
                for pk, pv in filt.get("params", {}).items():
                    _add_prop(f_el, pk, str(pv))

            _add_prop(entry, "kdenlive:id", clip_kid.get(cid, cid))
            prev_end = pos + clip_entry.get("out", 0) - clip_entry.get("in", 0)

        # Playlist 2: empty (dual playlist for mixes)
        pl2 = ET.SubElement(root, "playlist", {"id": f"playlist{track['id'] * 2 + 1}"})
        if is_audio:
            _add_prop(pl2, "kdenlive:audio_track", "1")

        # Wrapping tractor
        track_dur = track_durs[track["id"]]
        tractor = ET.SubElement(root, "tractor", {"id": tractor_id, "in": "0", "out": str(track_dur)})
        if is_audio:
            _add_prop(tractor, "kdenlive:audio_track", "1")
        if track.get("name"):
            _add_prop(tractor, "kdenlive:track_name", track["name"])

        if track.get("hide"):
            hide = "both"
        elif is_audio and track.get("mute"):
            hide = "both"
        elif is_audio:
            hide = "video"
        else:
            hide = "audio"
        ET.SubElement(tractor, "track", {"hide": hide, "producer": pl1.get("id")})
        ET.SubElement(tractor, "track", {"hide": hide, "producer": pl2.get("id")})

        if is_audio:
            filter_counter = _add_disabled_filter(tractor, "volume", filter_counter)
            filter_counter = _add_disabled_filter(tractor, "panner", filter_counter)
            filter_counter = _add_disabled_filter(tractor, "audiolevel", filter_counter)

        track_tractor_ids.append(tractor_id)
    return chain_counter, filter_counter
def _build_bin_clips(bin_chain_ids, bin_clips, chain_counter, clip_kid, fps_den, fps_num, root):
    for clip in bin_clips:
        bin_chain_id = f"chain{chain_counter}"
        chain_counter += 1
        bin_chain_ids[clip["id"]] = bin_chain_id
        dur = seconds_to_frames(clip.get("duration", 0), fps_num, fps_den)
        chain = ET.SubElement(root, "chain", {"id": bin_chain_id, "in": "0", "out": str(max(dur - 1, 0))})
        _add_prop(chain, "length", str(dur))
        _add_prop(chain, "eof", "pause")
        _add_prop(chain, "resource", clip.get("source", ""))
        _set_producer_props(chain, clip.get("type", "video"))
        _add_prop(chain, "kdenlive:folderid", "-1")
        _add_prop(chain, "kdenlive:id", clip_kid[clip["id"]])
        _add_prop(chain, "mute_on_pause", "0")
        _add_prop(chain, "kdenlive:clip_type", str(_clip_type_num(clip.get("type", "video"))))
        if clip.get("name"):
            _add_prop(chain, "kdenlive:clipname", clip["name"])
