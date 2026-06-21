# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTimelineMixin0:
    def test_list_tracks_initial(self, session):
        assert len(tl_mod.list_tracks(session)) >= 1
    def test_add_video_track(self, session):
        initial = len(tl_mod.list_tracks(session))
        result = tl_mod.add_track(session, "video", "V1")
        assert result["type"] == "video"
        assert len(tl_mod.list_tracks(session)) == initial + 1
    def test_add_audio_track(self, session):
        initial = len(tl_mod.list_tracks(session))
        result = tl_mod.add_track(session, "audio", "A1")
        assert result["type"] == "audio"
        assert len(tl_mod.list_tracks(session)) == initial + 1
    def test_add_invalid_track_type(self, session):
        with pytest.raises(ValueError):
            tl_mod.add_track(session, "invalid")
    def test_remove_track(self, session):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        count = len(tl_mod.list_tracks(session))
        tl_mod.remove_track(session, count - 1)
        assert len(tl_mod.list_tracks(session)) == count - 1
    def test_remove_track_middle(self, session):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        tl_mod.add_track(session, "audio", "A1")
        count = len(tl_mod.list_tracks(session))
        tl_mod.remove_track(session, 2)
        assert len(tl_mod.list_tracks(session)) == count - 1
    def test_remove_background_track_fails(self, session):
        with pytest.raises(IndexError):
            tl_mod.remove_track(session, 0)
    def test_add_clip_not_imported(self, session_with_track):
        with pytest.raises(ValueError, match="not imported"):
            tl_mod.add_clip(session_with_track, "clip999", 1)
    def test_add_and_list_clip(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:05.000")
        clips = tl_mod.list_clips(session_with_track, 1)
        assert len([c for c in clips if c.get("clip_index") is not None]) == 1
    def test_remove_clip(self, session_with_clip):
        tl_mod.remove_clip(session_with_clip, 1, 0)
        clips = [c for c in tl_mod.list_clips(session_with_clip, 1)
                 if c.get("clip_index") is not None]
        assert len(clips) == 0
    def test_remove_clip_without_ripple_preserves_inclusive_duration(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000")
        tl_mod.remove_clip(session_with_track, 1, 0, ripple=False)
        blank = next(item for item in tl_mod.list_clips(session_with_track, 1)
                     if item.get("type") == "blank")
        assert parse_time_input(blank["length"]) == timecode_to_frames("00:00:01.000") + 1
    def test_trim_clip(self, session_with_clip):
        result = tl_mod.trim_clip(session_with_clip, 1, 0,
                                  in_point="00:00:02.000", out_point="00:00:04.000")
        assert result["new_in"] == "00:00:02.000"
        assert result["new_out"] == "00:00:04.000"
    def test_split_clip(self, session_with_clip):
        result = tl_mod.split_clip(session_with_clip, 1, 0, "00:00:03.000")
        expected_first_out = frames_to_timecode(timecode_to_frames("00:00:03.000") - 1)
        assert result["first_clip"]["out"] == expected_first_out
        assert result["second_clip"]["in"] == "00:00:03.000"
        clips = [c for c in tl_mod.list_clips(session_with_clip, 1)
                 if c.get("clip_index") is not None]
        assert len(clips) == 2
    def test_move_clip(self, session, dummy_file):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        clip_id = media_mod.import_media(session, dummy_file)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")
        tl_mod.move_clip(session, 1, 0, 2)
        assert len([c for c in tl_mod.list_clips(session, 1)
                    if c.get("clip_index") is not None]) == 0
        assert len([c for c in tl_mod.list_clips(session, 2)
                    if c.get("clip_index") is not None]) == 1
    def test_set_track_name(self, session_with_track):
        result = tl_mod.set_track_name(session_with_track, 1, "My Track")
        assert result["name"] == "My Track"
    def test_mute_unmute(self, session):
        tl_mod.add_track(session, "audio")
        idx = len(tl_mod.list_tracks(session)) - 1
        assert tl_mod.set_track_mute(session, idx, True)["mute"] is True
        assert tl_mod.set_track_mute(session, idx, False)["mute"] is False
    def test_show_timeline(self, session_with_track):
        result = tl_mod.show_timeline(session_with_track)
        assert "tracks" in result
        assert "fps_num" in result
    def test_add_blank(self, session_with_track):
        assert tl_mod.add_blank(session_with_track, 1, "00:00:02.000")["action"] == "add_blank"
    def test_add_clip_at_absolute_time(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        result = tl_mod.add_clip(
            session_with_track, clip_id, 1,
            in_point="00:00:00.000", out_point="00:00:02.000",
            at_time="00:00:05.000",
        )
        assert result["at_time"] == "00:00:05.000"
        clips = tl_mod.list_clips(session_with_track, 1)
        assert clips[0]["type"] == "blank"
        assert abs(
            parse_time_input(clips[0]["length"]) - parse_time_input("00:00:05.000")
        ) <= 1
        assert clips[1]["clip_index"] == 0
