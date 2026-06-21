# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTimelineMixin2:
    def test_remove_middle_track_no_self_referencing_qtblend(self, session):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        tl_mod.add_track(session, "video", "V3")
        tl_mod.remove_track(session, 2)
        for trans in session.get_main_tractor().findall("transition"):
            if get_property(trans, "mlt_service", "") == "qtblend":
                a = int(get_property(trans, "a_track", "0") or "0")
                b = int(get_property(trans, "b_track", "0") or "0")
                assert a != b
    def test_add_clip_without_ffprobe_no_hardcoded_duration(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        result = tl_mod.add_clip(session_with_track, clip_id, 1, in_point="00:00:00.000")
        chain = find_element_by_id(session_with_track.root, result["chain_id"])
        assert chain is not None
        assert chain.get("out", "") != "00:00:10.000"
    def test_empty_timeline_resets_tractor_out(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        assert session_with_track.get_main_tractor().get("out") != "00:00:00.000"
        tl_mod.remove_clip(session_with_track, 1, 0)
        assert session_with_track.get_main_tractor().get("out", "00:00:00.000") == "00:00:00.000"
    def test_add_clip_position_skips_transitions(self, session_with_three_clips, dummy_file, tmp_path):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        f2 = str(tmp_path / "second.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_three_clips, f2)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id2, 1, position=3,
                        in_point="00:00:00.000", out_point="00:00:05.000")
        playlist = tl_mod._get_track_playlist(session_with_three_clips, 1)
        real = [e for e in get_playlist_entries(playlist)
                if e["type"] == "entry"
                and not tl_mod.is_transition_entry_by_dict(e, session_with_three_clips.root)]
        assert len(real) == 4
        assert len(trans_mod.list_transitions(session_with_three_clips)) == 1
    def test_remove_clip_non_ripple_after_transition(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.remove_clip(session_with_three_clips, 1, 2, ripple=False)
        playlist = tl_mod._get_track_playlist(session_with_three_clips, 1)
        entries = get_playlist_entries(playlist)
        blanks = [e for e in entries if e["type"] == "blank"]
        assert len(blanks) == 1
        real = [e for e in entries if e["type"] == "entry"
                and not tl_mod.is_transition_entry_by_dict(e, session_with_three_clips.root)]
        assert len(real) == 2
    def test_insert_before_transitioned_clip_removes_old_transition(self, session_with_three_clips, tmp_path):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        f2 = str(tmp_path / "new.mp4")
        Path(f2).write_bytes(b"dummy")
        clip_id2 = media_mod.import_media(session_with_three_clips, f2)["clip_id"]
        tl_mod.add_clip(session_with_three_clips, clip_id2, 1, position=1,
                        in_point="00:00:00.000", out_point="00:00:05.000")
        playlist = tl_mod._get_track_playlist(session_with_three_clips, 1)
        trans_entries = [c for c in playlist
                         if c.tag == "entry" and tl_mod.is_transition_entry(c, session_with_three_clips.root)]
        assert len(trans_entries) == 0
    def test_move_clip_before_transition_removes_old_transition(self, session, dummy_file, tmp_path):
        f2 = str(tmp_path / "b.mp4")
        Path(f2).write_bytes(b"dummy")
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        clip_id = media_mod.import_media(session, dummy_file)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session, "dissolve", track_index=1, clip_a_index=0, duration_frames=14)
        clip_id2 = media_mod.import_media(session, f2)["clip_id"]
        tl_mod.add_clip(session, clip_id2, 2, "00:00:00.000", "00:00:10.000")
        tl_mod.move_clip(session, 2, 0, 1, 1)
        playlist = tl_mod._get_track_playlist(session, 1)
        trans_entries = [c for c in playlist
                         if c.tag == "entry" and tl_mod.is_transition_entry(c, session.root)]
        assert len(trans_entries) == 0
    def test_move_clip_uses_restored_in_out(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.add_track(session_with_three_clips, "video", "V2")
        orig_out = parse_time_input("00:00:10.000", 30000, 1001)
        tl_mod.move_clip(session_with_three_clips, 1, 0, 2)
        clips = tl_mod.list_clips(session_with_three_clips, 2)
        assert len(clips) == 1
        assert abs(parse_time_input(clips[0]["out"], 30000, 1001) - orig_out) <= 1
    def test_split_clip_with_transition_uses_correct_out(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        orig_out = parse_time_input("00:00:10.000", 30000, 1001)
        result = tl_mod.split_clip(session_with_three_clips, 1, 0, "00:00:05.000")
        expected_first_out = frames_to_timecode(timecode_to_frames("00:00:05.000") - 1)
        assert result["first_clip"]["out"] == expected_first_out
        assert abs(parse_time_input(result["second_clip"]["out"], 30000, 1001) - orig_out) <= 1
