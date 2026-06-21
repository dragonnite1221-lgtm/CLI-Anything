# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTransitionsMixin2:
    def test_insert_then_remove_transition_restores_correct_clips(self, session_with_three_clips, tmp_path):
        fps_num, fps_den = 30000, 1001
        tractor = session_with_three_clips.get_main_tractor()
        pl = find_element_by_id(session_with_three_clips.root,
                                get_tractor_tracks(tractor)[1].get("producer"))
        entries = [c for c in pl if c.tag == "entry" and not tl_mod.is_transition_entry(c, session_with_three_clips.root)]
        orig_a_out = parse_time_input(entries[0].get("out"), fps_num, fps_den)
        orig_b_in = parse_time_input(entries[1].get("in"), fps_num, fps_den)
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        f2 = str(tmp_path / "new.mp4")
        Path(f2).write_bytes(b"newclip")
        clip_id2 = media_mod.import_media(session_with_three_clips, f2)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id2, 1, position=2,
                        in_point="00:00:00.000", out_point="00:00:03.000")
        trans_mod.remove_transition(session_with_three_clips, 0)
        entries_after = [c for c in pl if c.tag == "entry" and not tl_mod.is_transition_entry(c, session_with_three_clips.root)]
        assert abs(parse_time_input(entries_after[0].get("out"), fps_num, fps_den) - orig_a_out) <= 1
        assert abs(parse_time_input(entries_after[1].get("in"), fps_num, fps_den) - orig_b_in) <= 1
    def test_remove_transition_odd_frames_no_loss(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        fps_num, fps_den = 30000, 1001
        trans_frames = 15
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=trans_frames)
        pl = tl_mod._get_track_playlist(session_with_track, 1)
        entries = [c for c in pl if c.tag == "entry" and not tl_mod.is_transition_entry(c, session_with_track.root)]
        trimmed_a_out = parse_time_input(entries[0].get("out"), fps_num, fps_den)
        trimmed_b_in = parse_time_input(entries[1].get("in"), fps_num, fps_den)
        trans_mod.remove_transition(session_with_track, 0)
        clip_entries = [c for c in pl if c.tag == "entry" and not tl_mod.is_transition_entry(c, session_with_track.root)]
        restored_a_out = parse_time_input(clip_entries[0].get("out"), fps_num, fps_den)
        restored_b_in = parse_time_input(clip_entries[1].get("in"), fps_num, fps_den)
        total_restored = (restored_a_out - trimmed_a_out) + (trimmed_b_in - restored_b_in)
        assert total_restored == trans_frames
    def test_trim_clip_b_reanchors_track_a_in_transition(self, session_with_track, dummy_file, tmp_path):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        f2 = str(tmp_path / "b_reanchor.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_track, f2)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_track, clip_id2, 1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        trans_entries = [c for c in list(session_with_track.root)
                         if c.tag == "tractor" and get_property(c, "shotcut:transition") is not None]
        old_a_in = trans_entries[0].findall("track")[0].get("in")
        tl_mod.trim_clip(session_with_track, 1, 1, in_point="00:00:00.200")
        new_a_in = trans_entries[0].findall("track")[0].get("in")
        assert new_a_in != old_a_in
    def test_remove_transition_after_retime_uses_track_bounds(self, session_with_track, dummy_file, tmp_path):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        f2 = str(tmp_path / "retime_bounds.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_track, f2)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_track, clip_id2, 1, "00:00:05.000", "00:00:15.000")
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.trim_clip(session_with_track, 1, 0, out_point="00:00:09.700")
        clips = [c for c in tl_mod.list_clips(session_with_track, 1) if "clip_index" in c]
        entry_a_out = clips[0]["out"]
        entry_b_in = clips[1]["in"]
        fps_num, fps_den = 30000, 1001
        trans_mod.remove_transition(session_with_track, 0)
        clips_after = [c for c in tl_mod.list_clips(session_with_track, 1) if "clip_index" in c]
        assert parse_time_input(clips_after[0]["out"], fps_num, fps_den) - \
               parse_time_input(entry_a_out, fps_num, fps_den) > 0
        assert parse_time_input(entry_b_in, fps_num, fps_den) - \
               parse_time_input(clips_after[1]["in"], fps_num, fps_den) > 0
    def test_list_transitions_shows_mix_params(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        transitions = trans_mod.list_transitions(session_with_track)
        assert len(transitions) == 1
        assert "progressive" in transitions[0]["params"]
