# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestFilters:
    def test_add_and_remove_filter(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0)
        filt_mod.add_filter(session, "sepia", track_index=1, clip_index=0)

        remaining = filt_mod.list_filters(session, track_index=1, clip_index=0)
        assert len(remaining) == 2

        result = filt_mod.remove_filter(session, 0, track_index=1, clip_index=0)
        assert result["service"] == "brightness"

        remaining = filt_mod.list_filters(session, track_index=1, clip_index=0)
        assert len(remaining) == 1
        assert remaining[0]["service"] == "sepia"

    def test_filter_with_custom_params(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        result = filt_mod.add_filter(session, "text", track_index=1, clip_index=0,
                                     params={
                                         "argument": "Hello World",
                                         "size": "72",
                                         "fgcolour": "#ff0000ff",
                                         "halign": "center",
                                         "valign": "bottom",
                                     })
        assert result["params"]["argument"] == "Hello World"
        assert result["params"]["size"] == "72"

    def test_set_filter_param(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")
        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0)

        result = filt_mod.set_filter_param(session, 0, "level", "0.3",
                                            track_index=1, clip_index=0)
        assert result["old_value"] == "1.0"
        assert result["new_value"] == "0.3"

    def test_filter_on_track_level(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        result = filt_mod.add_filter(session, "brightness", track_index=1)
        assert result["target"] == "track 1"
