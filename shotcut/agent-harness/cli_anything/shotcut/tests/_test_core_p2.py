# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestFilters:
    def test_filter_catalog_completeness(self):
        result = filt_mod.list_available_filters()
        assert len(result) >= 50
        names = [f["name"] for f in result]
        categories = set(f["category"] for f in result)
        assert "audio" in categories
        assert "sharpen" in names or "brightness" in names
        color_filters = [n for n in names if n in
                         ("color-grading", "levels", "white-balance",
                          "contrast", "gamma", "vibrance", "invert",
                          "grayscale", "threshold", "posterize")]
        assert len(color_filters) >= 3

    def test_list_by_category(self):
        video = filt_mod.list_available_filters("video")
        audio = filt_mod.list_available_filters("audio")
        assert all(f["category"] == "video" for f in video)
        assert all(f["category"] == "audio" for f in audio)

    def test_get_filter_info(self):
        info = filt_mod.get_filter_info("brightness")
        assert info["service"] == "brightness"
        assert "params" in info

    def test_get_unknown_filter(self):
        with pytest.raises(ValueError):
            filt_mod.get_filter_info("nonexistent_filter")

    def test_filter_info_has_params(self):
        info = filt_mod.get_filter_info("sharpen")
        assert "params" in info
        assert info["name"] == "sharpen"

    @pytest.mark.parametrize("filter_name", ["sharpen", "vignette", "grayscale", "invert"])
    def test_add_various_filters(self, filter_name, session_with_clip):
        result = filt_mod.add_filter(session_with_clip, filter_name,
                                     track_index=1, clip_index=0)
        assert result["action"] == "add_filter"
        assert result["filter_name"] == filter_name

    def test_add_filter_to_clip(self, session_with_clip):
        filt_mod.add_filter(session_with_clip, "brightness", track_index=1,
                           clip_index=0, params={"level": "1.5"})
        filters = filt_mod.list_filters(session_with_clip, track_index=1, clip_index=0)
        assert len(filters) == 1
        assert filters[0]["service"] == "brightness"

    def test_add_filter_to_track(self, session_with_clip):
        result = filt_mod.add_filter(session_with_clip, "volume", track_index=1)
        assert result["target"] == "track 1"
        assert len(filt_mod.list_filters(session_with_clip, track_index=1)) >= 1

    def test_add_global_filter(self, session):
        assert filt_mod.add_filter(session, "brightness")["target"] == "global"

    def test_remove_filter(self, session_with_clip):
        filt_mod.add_filter(session_with_clip, "brightness", track_index=1, clip_index=0)
        filt_mod.remove_filter(session_with_clip, 0, track_index=1, clip_index=0)
        assert len(filt_mod.list_filters(session_with_clip, track_index=1, clip_index=0)) == 0

    def test_set_filter_param(self, session_with_clip):
        filt_mod.add_filter(session_with_clip, "brightness", track_index=1, clip_index=0)
        result = filt_mod.set_filter_param(session_with_clip, 0, "level", "0.5",
                                           track_index=1, clip_index=0)
        assert result["new_value"] == "0.5"

    def test_undo_add_filter(self, session_with_clip):
        filt_mod.add_filter(session_with_clip, "brightness", track_index=1, clip_index=0)
        assert len(filt_mod.list_filters(session_with_clip, track_index=1, clip_index=0)) == 1
        session_with_clip.undo()
        assert len(filt_mod.list_filters(session_with_clip, track_index=1, clip_index=0)) == 0

    def test_set_volume_envelope(self, session_with_clip):
        result = filt_mod.set_volume_envelope(
            session_with_clip,
            [("00:00:00.000", "1.0"), ("00:00:03.000", "0.25"), ("00:00:04.000", "1.0")],
            track_index=1,
        )
        assert result["action"] == "set_volume_envelope"
        filters = filt_mod.list_filters(session_with_clip, track_index=1)
        assert filters[0]["service"] == "volume"
        assert filters[0]["params"]["level"].count("=") == 3

    def test_duck_volume(self, session_with_clip):
        result = filt_mod.duck_volume(
            session_with_clip,
            [("00:00:01.000", "00:00:02.000")],
            track_index=1,
            normal_level=1.0,
            duck_level=0.3,
        )
        assert result["action"] == "duck_volume"
        filters = filt_mod.list_filters(session_with_clip, track_index=1)
        assert "0.3" in filters[0]["params"]["level"]

    def test_duck_window_dotdot_split(self):
        windows_cli = ["00:00:01.000..00:00:03.000"]
        parsed = []
        for w in windows_cli:
            start_tc, end_tc = w.split("..", 1)
            parsed.append((start_tc, end_tc))
        assert parsed == [("00:00:01.000", "00:00:03.000")]
