# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestTimelineEdgeCases:
    def test_add_blank(self, session_with_clip):
        result = tl_mod.add_blank(session_with_clip, 1, "00:00:02.000")
        assert result["action"] == "add_blank"
        clips = tl_mod.list_clips(session_with_clip, 1)
        blanks = [c for c in clips if c.get("type") == "blank"]
        assert len(blanks) == 1

    def test_set_track_mute(self, session_with_track):
        result = tl_mod.set_track_mute(session_with_track, 1, True)
        assert result["action"] == "set_track_mute"
        tracks = tl_mod.list_tracks(session_with_track)
        audio_track = [t for t in tracks if t["index"] == 1][0]
        assert "audio" in audio_track.get("hide", "")

    def test_set_track_unmute(self, session_with_track):
        tl_mod.set_track_mute(session_with_track, 1, True)
        tl_mod.set_track_mute(session_with_track, 1, False)
        tracks = tl_mod.list_tracks(session_with_track)
        audio_track = [t for t in tracks if t["index"] == 1][0]
        assert "audio" not in audio_track.get("hide", "")

    def test_set_track_hidden(self, session_with_track):
        result = tl_mod.set_track_hidden(session_with_track, 1, True)
        assert result["action"] == "set_track_hidden"
        tracks = tl_mod.list_tracks(session_with_track)
        video_track = [t for t in tracks if t["index"] == 1][0]
        assert "video" in video_track.get("hide", "")

    def test_set_track_unhidden(self, session_with_track):
        tl_mod.set_track_hidden(session_with_track, 1, True)
        tl_mod.set_track_hidden(session_with_track, 1, False)
        tracks = tl_mod.list_tracks(session_with_track)
        video_track = [t for t in tracks if t["index"] == 1][0]
        assert "video" not in video_track.get("hide", "")

    def test_set_track_hidden_while_muted(self, session_with_track):
        tl_mod.set_track_mute(session_with_track, 1, True)
        tl_mod.set_track_hidden(session_with_track, 1, True)
        tracks = tl_mod.list_tracks(session_with_track)
        track = [t for t in tracks if t["index"] == 1][0]
        assert track["hide"] == "both"

    def test_unhide_while_both(self, session_with_track):
        tl_mod.set_track_mute(session_with_track, 1, True)
        tl_mod.set_track_hidden(session_with_track, 1, True)
        tl_mod.set_track_hidden(session_with_track, 1, False)
        tracks = tl_mod.list_tracks(session_with_track)
        track = [t for t in tracks if t["index"] == 1][0]
        assert track["hide"] == "audio"

    def test_remove_adjacent_transitions_both_sides(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=1, duration_frames=14)
        tl_mod.remove_clip(session_with_three_clips, 1, 1)
        remaining = trans_mod.list_transitions(session_with_three_clips)
        assert len(remaining) == 0
        clips = tl_mod.list_clips(session_with_three_clips, 1)
        real = [c for c in clips if "clip_index" in c]
        assert len(real) == 2

    def test_remove_adjacent_transitions_preserves_distant(self, session_with_three_clips):
        trans_mod.add_transition(session_with_three_clips, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        tl_mod.remove_clip(session_with_three_clips, 1, 2)
        remaining = trans_mod.list_transitions(session_with_three_clips)
        assert len(remaining) == 1

    def test_set_track_name(self, session_with_track):
        tl_mod.set_track_name(session_with_track, 1, "MyTrack")
        tracks = tl_mod.list_tracks(session_with_track)
        assert tracks[1]["name"] == "MyTrack"

    def test_remove_clip_no_ripple(self, session_with_two_clips):
        tl_mod.remove_clip(session_with_two_clips, 1, 0, ripple=False)
        clips = tl_mod.list_clips(session_with_two_clips, 1)
        blanks = [c for c in clips if c.get("type") == "blank"]
        real = [c for c in clips if "clip_index" in c]
        assert len(blanks) == 1
        assert len(real) == 1

    def test_move_clip(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:05.000", "00:00:10.000")
        tl_mod.move_clip(session_with_track, 1, 0, to_track=1, to_position=1)
        clips = tl_mod.list_clips(session_with_track, 1)
        real = [c for c in clips if "clip_index" in c]
        assert len(real) == 2

    def test_list_tracks_invalid_index(self, session_with_track):
        with pytest.raises(IndexError):
            tl_mod.set_track_name(session_with_track, 99, "bad")

    def test_list_tracks_no_project(self):
        with pytest.raises(RuntimeError):
            tl_mod.list_tracks(Session())

    def test_show_timeline_no_project(self):
        with pytest.raises(RuntimeError):
            tl_mod.show_timeline(Session())

    def test_add_clip_no_project(self, dummy_file):
        with pytest.raises(ValueError, match="not imported"):
            tl_mod.add_clip(Session(), "clip0", 1, None, None)

    def test_add_clip_not_imported(self, session_with_track):
        with pytest.raises(ValueError, match="not imported"):
            tl_mod.add_clip(session_with_track, "clip999", 1, None, None)

    def test_remove_clip_out_of_range(self, session_with_clip):
        with pytest.raises(IndexError):
            tl_mod.remove_clip(session_with_clip, 1, 99)

    def test_get_track_playlist_invalid(self, session):
        with pytest.raises(IndexError, match="out of range"):
            tl_mod._get_track_playlist(session, 99)
