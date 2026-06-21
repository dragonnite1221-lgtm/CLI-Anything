# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403
# fmt: off
from .mlt_xml_p1 import _add_prop, _track_index, seconds_to_frames  # noqa: E402,E501
# fmt: on


def _build_transitions(fps_den, fps_num, orig_to_seq, project, seq, tracks, transition_counter):
    for td in project.get("transitions", []):
        pos_f = seconds_to_frames(td.get("position", 0), fps_num, fps_den)
        dur_f = seconds_to_frames(td.get("duration", 1), fps_num, fps_den)
        a_orig = _track_index(tracks, td["track_a"])
        b_orig = _track_index(tracks, td["track_b"])
        a_idx = orig_to_seq.get(a_orig, a_orig) + 1
        b_idx = orig_to_seq.get(b_orig, b_orig) + 1
        trans = ET.SubElement(seq, "transition", {
            "id": f"transition{transition_counter}",
            "mlt_service": td.get("mlt_service", ""),
            "in": str(pos_f),
            "out": str(pos_f + dur_f),
            "a_track": str(a_idx),
            "b_track": str(b_idx),
        })
        transition_counter += 1
        _add_prop(trans, "kdenlive_id", td.get("type", ""))
        for pk, pv in td.get("params", {}).items():
            if pk == "duration":
                continue
            _add_prop(trans, pk, str(pv))
