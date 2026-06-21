# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTransitionsMixin0:
    def test_list_available_transitions(self):
        names = [t["name"] for t in trans_mod.list_available_transitions()]
        assert len(names) >= 10
        assert "dissolve" in names
        assert "wipe-left" in names
    def test_list_by_category_video(self):
        names = [t["name"] for t in trans_mod.list_available_transitions("video")]
        assert "dissolve" in names
        assert "crossfade" not in names
    def test_list_by_category_audio(self):
        names = [t["name"] for t in trans_mod.list_available_transitions("audio")]
        assert "crossfade" in names
    def test_get_transition_info(self):
        info = trans_mod.get_transition_info("dissolve")
        assert info["service"] == "luma"
        assert "params" in info
    def test_get_transition_info_invalid(self):
        with pytest.raises(ValueError):
            trans_mod.get_transition_info("nonexistent_transition")
    def test_add_transition(self, session_with_two_clips):
        result = trans_mod.add_transition(session_with_two_clips, "dissolve",
                                          track_index=1, clip_a_index=0, duration_frames=14)
        assert result["service"] == "luma"
    def test_add_transition_with_params(self, session_with_two_clips):
        result = trans_mod.add_transition(session_with_two_clips, "dissolve",
                                          track_index=1, clip_a_index=0,
                                          duration_frames=14, params={"softness": "0.5"})
        assert result["params"]["softness"] == "0.5"
    def test_add_wipe_transition(self, session_with_two_clips):
        result = trans_mod.add_transition(session_with_two_clips, "wipe-left",
                                          track_index=1, clip_a_index=0)
        assert result["params"]["resource"] == "%luma01.pgm"
    def test_add_transition_invalid_track(self, session_with_two_clips):
        with pytest.raises(IndexError):
            trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=99, clip_a_index=0)
    def test_add_raw_service_transition(self, session_with_two_clips):
        assert trans_mod.add_transition(
            session_with_two_clips, "luma", track_index=1, clip_a_index=0,
            duration_frames=14, params={"softness": "0.3"})["service"] == "luma"
    def test_list_transitions_empty(self, session):
        assert trans_mod.list_transitions(session) == []
    def test_list_transitions_after_add(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        result = trans_mod.list_transitions(session_with_two_clips)
        assert len(result) >= 1
        assert result[-1]["service"] == "luma"
    def test_remove_transition(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        baseline = len(trans_mod.list_transitions(session_with_two_clips))
        trans_mod.remove_transition(session_with_two_clips, 0)
        assert len(trans_mod.list_transitions(session_with_two_clips)) == baseline - 1
    def test_remove_transition_invalid_index(self, session):
        with pytest.raises(IndexError):
            trans_mod.remove_transition(session, 0)
    def test_set_transition_param(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        result = trans_mod.set_transition_param(session_with_two_clips, 0, "softness", "0.8")
        assert result["new_value"] == "0.8"
    def test_undo_add_transition(self, session_with_two_clips):
        baseline = len(trans_mod.list_transitions(session_with_two_clips))
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        session_with_two_clips.undo()
        assert len(trans_mod.list_transitions(session_with_two_clips)) == baseline
    def test_multiple_transitions(self, session_with_three_clips, dummy_file):
        clip_id = media_mod.import_media(session_with_three_clips, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id,
                        1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1, clip_a_index=0)
        trans_mod.add_transition(session_with_three_clips, "wipe-left", track_index=1, clip_a_index=1)
        assert len(trans_mod.list_transitions(session_with_three_clips)) >= 2
    def test_transition_tractor_before_playlist(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        playlist = tl_mod._get_track_playlist(session_with_two_clips, 1)
        trans_tractors = [c for c in session_with_two_clips.root
                          if c.tag == "tractor" and c.get("id") != "tractor0"
                          and get_property(c, "shotcut:transition")]
        assert len(trans_tractors) == 1
        assert list(session_with_two_clips.root).index(trans_tractors[0]) < \
               list(session_with_two_clips.root).index(playlist)
    def test_transition_tractor_has_in_out(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        tt = [c for c in session_with_two_clips.root
              if c.tag == "tractor" and c.get("id") != "tractor0"
              and get_property(c, "shotcut:transition")][0]
        assert tt.get("in") == "00:00:00.000"
        assert tt.get("out") is not None
    def test_add_track_after_transition(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        tl_mod.add_track(session_with_two_clips, "video", "V2")
        assert len(get_tractor_tracks(session_with_two_clips.get_main_tractor())) == 3
    def test_list_transitions_has_track_producers(self, session_with_two_clips):
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1, clip_a_index=0)
        assert len(trans_mod.list_transitions(session_with_two_clips)[0]["track_producers"]) == 2
    def test_remove_transition_restores_clip_lengths(self, session_with_two_clips):
        fps_num, fps_den = 30000, 1001
        tractor = session_with_two_clips.get_main_tractor()
        pl = find_element_by_id(session_with_two_clips.root,
                                get_tractor_tracks(tractor)[1].get("producer"))
        entries = [c for c in pl if c.tag == "entry"]
        orig_a_out = parse_time_input(entries[0].get("out"), fps_num, fps_den)
        orig_b_in = parse_time_input(entries[1].get("in"), fps_num, fps_den)
        trans_mod.add_transition(session_with_two_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        trans_mod.remove_transition(session_with_two_clips, 0)
        clip_entries = [c for c in pl if c.tag == "entry"]
        assert abs(parse_time_input(clip_entries[0].get("out"), fps_num, fps_den) - orig_a_out) <= 1
        assert abs(parse_time_input(clip_entries[1].get("in"), fps_num, fps_den) - orig_b_in) <= 1
