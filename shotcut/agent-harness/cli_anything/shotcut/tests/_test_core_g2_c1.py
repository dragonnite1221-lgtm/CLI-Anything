# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestTimelineMixin1:
    def test_add_clip_at_absolute_time_rejects_overlap(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(
            session_with_track, clip_id, 1,
            in_point="00:00:00.000", out_point="00:00:05.000",
        )
        with pytest.raises(RuntimeError, match="overlaps an existing clip"):
            tl_mod.add_clip(
                session_with_track, clip_id, 1,
                in_point="00:00:00.000", out_point="00:00:02.000",
                at_time="00:00:03.000",
            )
    def test_add_clip_at_time_uses_inclusive_duration(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000")
        next_start = frames_to_timecode(timecode_to_frames("00:00:01.000") + 1)
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000",
                        at_time=next_start)
        items = tl_mod.list_clips(session_with_track, 1)
        assert len([item for item in items if item.get("type") == "blank"]) == 0
        assert len([item for item in items if item.get("clip_index") is not None]) == 2
    def test_add_clip_at_time_inserts_gap(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        result = tl_mod.add_clip(
            session_with_track, clip_id, 1,
            in_point="00:00:00.000", out_point="00:00:02.000",
            at_time="00:00:08.000",
        )
        assert result["at_time"] == "00:00:08.000"
        clips = tl_mod.list_clips(session_with_track, 1)
        assert clips[0]["type"] == "blank"
        assert clips[1]["clip_index"] == 0
    def test_add_clip_at_time_rejects_overlap_after_clip(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(
            session_with_track, clip_id, 1,
            in_point="00:00:00.000", out_point="00:00:05.000",
        )
        with pytest.raises(RuntimeError, match="overlaps an existing clip"):
            tl_mod.add_clip(
                session_with_track, clip_id, 1,
                in_point="00:00:00.000", out_point="00:00:01.000",
                at_time="00:00:02.000",
            )
    def test_add_clip_at_boundary_between_clips(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        next_start = frames_to_timecode(timecode_to_frames("00:00:01.000") + 1)
        third_start = frames_to_timecode((timecode_to_frames("00:00:01.000") + 1) * 2)
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000")
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000",
                        at_time=next_start)
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000",
                        at_time=third_start)
        clips = tl_mod.list_clips(session_with_track, 1)
        real = [c for c in clips if c.get("clip_index") is not None]
        assert len(real) == 3
        playlist = session_with_track._track_playlists[1]
        children = list(playlist)
        entry_producers = [c.get("producer") for c in children if c.tag == "entry"]
        assert entry_producers == ["tl_clip0", "tl_clip0", "tl_clip0"]
    def test_add_clip_at_after_two_clips(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        next_start = frames_to_timecode(timecode_to_frames("00:00:01.000") + 1)
        third_start = frames_to_timecode((timecode_to_frames("00:00:01.000") + 1) * 2)
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000")
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000",
                        at_time=next_start)
        tl_mod.add_clip(session_with_track, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:01.000",
                        at_time=third_start)
        clips = tl_mod.list_clips(session_with_track, 1)
        real = [c for c in clips if c.get("clip_index") is not None]
        assert len(real) == 3
    def test_undo_add_track(self, session):
        initial = len(tl_mod.list_tracks(session))
        tl_mod.add_track(session, "video")
        assert len(tl_mod.list_tracks(session)) == initial + 1
        session.undo()
        assert len(tl_mod.list_tracks(session)) == initial
    def test_remove_track_updates_tractor_out(self, session, dummy_file):
        tl_mod.add_track(session, "video")
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, dummy_file)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session, clip_id, 2, "00:00:00.000", "00:00:30.000")
        tl_mod.remove_track(session, 2)
        tractor = session.get_main_tractor()
        out = parse_time_input(tractor.get("out", "0"), 30000, 1001)
        expected = parse_time_input("00:00:10.000", 30000, 1001)
        assert out <= expected + 1
    def test_remove_middle_track_decrements_higher_transition_indices(self, session):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        tl_mod.add_track(session, "video", "V3")
        tl_mod.remove_track(session, 2)
        remaining = get_tractor_tracks(session.get_main_tractor())
        max_idx = len(remaining) - 1
        for trans in session.get_main_tractor().findall("transition"):
            a = int(get_property(trans, "a_track", "0") or "0")
            b = int(get_property(trans, "b_track", "0") or "0")
            assert a <= max_idx
            assert b <= max_idx
