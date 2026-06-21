# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTransitionsMixin1:
    def test_add_transition_rejects_blank_gap(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_blank(session_with_track, 1, "00:00:02.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        with pytest.raises(ValueError, match="blank gap"):
            trans_mod.add_transition(session_with_track, "dissolve", track_index=1, clip_a_index=0)
    def test_audio_track_no_qtblend(self, session):
        tl_mod.add_track(session, "video")
        tl_mod.add_track(session, "audio")
        tractor = session.get_main_tractor()
        qtblend_audio = [t for t in tractor.findall("transition")
                         if get_property(t, "mlt_service") == "qtblend"
                         and get_property(t, "b_track") == "2"]
        assert len(qtblend_audio) == 0
        mix_audio = [t for t in tractor.findall("transition")
                     if get_property(t, "mlt_service") == "mix"
                     and get_property(t, "b_track") == "2"]
        assert len(mix_audio) == 1
    def test_remove_clip_cleans_adjacent_transitions(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=0)
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=1)
        assert len(trans_mod.list_transitions(session_with_three_clips)) == 2
        tl_mod.remove_clip(session_with_three_clips, 1, 1)
        assert len(trans_mod.list_transitions(session_with_three_clips)) == 0
    def test_trim_clip_updates_adjacent_transition(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=0)
        tl_mod.trim_clip(session_with_three_clips, 1, 0, out_point="00:00:05.000")
        trans_list = trans_mod.list_transitions(session_with_three_clips)
        if trans_list:
            trans_tractor = find_element_by_id(session_with_three_clips.root, trans_list[0]["id"])
            if trans_tractor is not None:
                track_a_out = parse_time_input(trans_tractor.findall("track")[0].get("out", "0"), 30000, 1001)
                clip_out = parse_time_input("00:00:05.000", 30000, 1001)
                assert track_a_out <= clip_out
    def test_remove_track_cleans_transition_tractors(self, session_with_three_clips, dummy_file, tmp_path):
        tl_mod.add_track(session_with_three_clips, "video", "V2")
        f2 = str(tmp_path / "v2.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_three_clips, f2)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id2, 2, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_three_clips, clip_id2, 2, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=2, clip_a_index=0)
        tl_mod.remove_track(session_with_three_clips, 2)
        assert len(trans_mod.list_transitions(session_with_three_clips)) == 0
        orphaned = [c for c in session_with_three_clips.root
                    if c.tag == "tractor" and c.get("id") != "tractor0"
                    and get_property(c, "shotcut:transition")]
        assert len(orphaned) == 0
    def test_trim_clip_retime_updates_all_transition_outs(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.trim_clip(session_with_three_clips, 1, 0, out_point="00:00:03.000")
        trans_list = trans_mod.list_transitions(session_with_three_clips)
        if trans_list:
            tt = find_element_by_id(session_with_three_clips.root, trans_list[0]["id"])
            if tt is not None:
                assert tt.get("out") == tt.findall("transition")[0].get("out")
    def test_trim_clip_in_point_shortens_transition(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.trim_clip(session_with_three_clips, 1, 1, in_point="00:00:09.990")
        for trans in trans_mod._get_user_transitions(session_with_three_clips.root):
            for t in trans.findall("track"):
                assert parse_time_input(t.get("in", "0"), 30000, 1001) <= \
                       parse_time_input(t.get("out", "0"), 30000, 1001)
    def test_crossfade_single_mix_transition(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "crossfade", track_index=1, clip_a_index=0)
        transitions = trans_mod._get_user_transitions(session_with_three_clips.root)
        mix_count = sum(1 for t in transitions[0].findall("transition")
                        if get_property(t, "mlt_service") == "mix")
        assert mix_count == 1
    def test_retime_gives_frames_back_to_other_clip(self, session_with_three_clips, tmp_path):
        f2 = str(tmp_path / "retime_test.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_three_clips, f2)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id2, 1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=2, duration_frames=100)
        tractor = session_with_three_clips.get_main_tractor()
        pl = find_element_by_id(session_with_three_clips.root,
                                get_tractor_tracks(tractor)[1].get("producer"))
        entries_before = [c for c in pl if c.tag == "entry"
                         and not tl_mod.is_transition_entry(c, session_with_three_clips.root)]
        b_in_before = parse_time_input(entries_before[3].get("in"), 30000, 1001)
        tl_mod.trim_clip(session_with_three_clips, 1, 2, out_point="00:00:07.000")
        assert len(trans_mod.list_transitions(session_with_three_clips)) == 1
        entries_after = [c for c in pl if c.tag == "entry"
                        and not tl_mod.is_transition_entry(c, session_with_three_clips.root)]
        b_in_after = parse_time_input(entries_after[3].get("in"), 30000, 1001)
        assert b_in_after < b_in_before
    def test_add_transition_rejects_duplicate(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=0)
        with pytest.raises(ValueError, match="already exists"):
            trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=0)
    def test_short_clip_transition_no_invalid_range(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:00.200")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:00.200")
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        for c in tl_mod.list_clips(session_with_track, 1):
            if "clip_index" in c:
                assert parse_time_input(c["out"], 30000, 1001) > parse_time_input(c["in"], 30000, 1001)
