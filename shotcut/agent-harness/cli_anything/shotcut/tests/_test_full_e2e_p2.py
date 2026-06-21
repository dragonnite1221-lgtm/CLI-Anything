# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestTimelineClips:
    def test_add_single_clip(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        result = tl_mod.add_clip(session, clip_id, 1,
                                 in_point="00:00:00.000", out_point="00:00:05.000")
        assert result["resource"] == os.path.abspath(video)
        clips = tl_mod.list_clips(session, 1)
        real_clips = [c for c in clips if "clip_index" in c]
        assert len(real_clips) == 1

    def test_add_multiple_clips_sequential(self, session, video):
        tl_mod.add_track(session, "video", "V1")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        for i in range(5):
            start = f"00:00:{i*2:02d}.000"
            end = f"00:00:{i*2+2:02d}.000"
            tl_mod.add_clip(session, clip_id, 1, in_point=start, out_point=end,
                            caption=f"Scene {i+1}")

        clips = tl_mod.list_clips(session, 1)
        real_clips = [c for c in clips if "clip_index" in c]
        assert len(real_clips) == 5
        assert real_clips[0]["caption"] == "Scene 1"

    def test_add_clip_at_position(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:02.000", caption="First")
        tl_mod.add_clip(session, clip_id, 1, "00:00:04.000", "00:00:06.000", caption="Third")
        tl_mod.add_clip(session, clip_id, 1, "00:00:02.000", "00:00:04.000",
                        position=1, caption="Second")

        clips = tl_mod.list_clips(session, 1)
        real_clips = [c for c in clips if "clip_index" in c]
        assert len(real_clips) == 3
        assert real_clips[0]["out"] == "00:00:02.000"
        assert real_clips[1]["out"] == "00:00:04.000"
        assert real_clips[2]["out"] == "00:00:06.000"

    def test_remove_clip_ripple(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        for i in range(3):
            tl_mod.add_clip(session, clip_id, 1, f"00:00:{i*2:02d}.000",
                            f"00:00:{i*2+2:02d}.000")

        tl_mod.remove_clip(session, 1, 1, ripple=True)
        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 2

    def test_remove_clip_no_ripple(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:03.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:03.000", "00:00:06.000")

        tl_mod.remove_clip(session, 1, 0, ripple=False)
        items = tl_mod.list_clips(session, 1)
        types = [item.get("type") for item in items if "type" in item]
        assert "blank" in types

    def test_trim_clip_both_ends(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        result = tl_mod.trim_clip(session, 1, 0,
                                  in_point="00:00:02.000", out_point="00:00:08.000")
        assert result["new_in"] == "00:00:02.000"
        assert result["new_out"] == "00:00:08.000"

    def test_split_and_remove(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.split_clip(session, 1, 0, "00:00:03.000")
        tl_mod.remove_clip(session, 1, 0, ripple=True)

        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 1
        assert clips[0]["in"] == "00:00:03.000"

    def test_move_clip_between_tracks(self, session, video):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        tl_mod.move_clip(session, 1, 0, 2)

        clips_v1 = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        clips_v2 = [c for c in tl_mod.list_clips(session, 2) if "clip_index" in c]
        assert len(clips_v1) == 0
        assert len(clips_v2) == 1

    def test_add_blank_gap(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:03.000")
        tl_mod.add_blank(session, 1, "00:00:02.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:03.000", "00:00:06.000")

        items = tl_mod.list_clips(session, 1)
        assert any(i.get("type") == "blank" for i in items)

    def test_add_transition_between_clips(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")

        trans_mod.add_transition(session, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        transitions = trans_mod.list_transitions(session)
        assert len(transitions) == 1
        assert transitions[0]["service"] == "luma"
