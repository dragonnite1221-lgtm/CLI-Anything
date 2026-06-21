# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestSession:
    def test_undo_redo_chain(self, session, video):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "audio", "A1")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        assert len(tl_mod.list_tracks(session)) == 3
        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 1

        session.undo()
        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 0

        session.undo()
        assert media_mod.list_media(session) == []

        session.undo()
        assert len(tl_mod.list_tracks(session)) == 2

        session.redo()
        assert len(tl_mod.list_tracks(session)) == 3

        session.redo()
        assert len(media_mod.list_media(session)) == 1

        session.redo()
        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 1

    def test_undo_clears_redo_on_new_action(self, session, video):
        tl_mod.add_track(session, "video")
        tl_mod.add_track(session, "audio")

        session.undo()
        assert session.redo()

        session.undo()
        tl_mod.add_track(session, "video", "V2")
        assert not session.redo()

    def test_undo_filter_operations(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0,
                            params={"level": "1.5"})
        assert len(filt_mod.list_filters(session, 1, 0)) == 1

        filt_mod.set_filter_param(session, 0, "level", "0.5",
                                   track_index=1, clip_index=0)

        session.undo()
        filters = filt_mod.list_filters(session, 1, 0)
        assert filters[0]["params"]["level"] == "1.5"

        session.undo()
        assert len(filt_mod.list_filters(session, 1, 0)) == 0
