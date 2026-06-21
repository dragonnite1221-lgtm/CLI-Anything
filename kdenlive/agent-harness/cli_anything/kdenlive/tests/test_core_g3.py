# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFilters:
    def _make_project_with_clip_on_track(self):
        proj = create_project()
        import_clip(proj, "/video.mp4", name="Test", duration=30.0)
        add_track(proj, track_type="video")
        add_clip_to_track(proj, 0, "clip0", out_point=30.0)
        return proj

    def test_add_filter(self):
        proj = self._make_project_with_clip_on_track()
        f = add_filter(proj, 0, 0, "brightness", {"level": 1.5})
        assert f["name"] == "brightness"
        assert f["params"]["level"] == 1.5
        assert f["mlt_service"] == "brightness"

    def test_add_filter_defaults(self):
        proj = self._make_project_with_clip_on_track()
        f = add_filter(proj, 0, 0, "blur")
        assert f["params"]["hblur"] == 2
        assert f["params"]["vblur"] == 2

    def test_add_filter_unknown(self):
        proj = self._make_project_with_clip_on_track()
        with pytest.raises(ValueError, match="Unknown filter"):
            add_filter(proj, 0, 0, "nonexistent")

    def test_add_filter_invalid_param(self):
        proj = self._make_project_with_clip_on_track()
        with pytest.raises(ValueError, match="Unknown parameters"):
            add_filter(proj, 0, 0, "brightness", {"bogus": 1})

    def test_add_filter_out_of_range(self):
        proj = self._make_project_with_clip_on_track()
        with pytest.raises(ValueError, match="out of range"):
            add_filter(proj, 0, 0, "brightness", {"level": 99.0})

    def test_remove_filter(self):
        proj = self._make_project_with_clip_on_track()
        add_filter(proj, 0, 0, "brightness")
        removed = remove_filter(proj, 0, 0, 0)
        assert removed["name"] == "brightness"
        assert len(proj["tracks"][0]["clips"][0]["filters"]) == 0

    def test_remove_filter_invalid_index(self):
        proj = self._make_project_with_clip_on_track()
        with pytest.raises(IndexError):
            remove_filter(proj, 0, 0, 0)

    def test_set_filter_param(self):
        proj = self._make_project_with_clip_on_track()
        add_filter(proj, 0, 0, "brightness")
        result = set_filter_param(proj, 0, 0, 0, "level", 2.0)
        assert result["params"]["level"] == 2.0

    def test_set_filter_param_invalid(self):
        proj = self._make_project_with_clip_on_track()
        add_filter(proj, 0, 0, "brightness")
        with pytest.raises(ValueError, match="Unknown parameter"):
            set_filter_param(proj, 0, 0, 0, "bogus", 1.0)

    def test_list_filters(self):
        proj = self._make_project_with_clip_on_track()
        add_filter(proj, 0, 0, "brightness")
        add_filter(proj, 0, 0, "contrast")
        filters = list_filters(proj, 0, 0)
        assert len(filters) == 2

    def test_list_available_all(self):
        avail = list_available()
        assert len(avail) == len(FILTER_REGISTRY)
        names = [f["name"] for f in avail]
        assert "brightness" in names
        assert "chroma_key" in names

    def test_list_available_by_category(self):
        avail = list_available(category="color")
        assert all(f["category"] == "color" for f in avail)

    def test_all_filters_have_mlt_service(self):
        for name, spec in FILTER_REGISTRY.items():
            assert "mlt_service" in spec, f"Filter '{name}' missing mlt_service"
            assert spec["mlt_service"], f"Filter '{name}' has empty mlt_service"

    def test_chroma_key_filter(self):
        proj = self._make_project_with_clip_on_track()
        f = add_filter(proj, 0, 0, "chroma_key", {"color": "#00ff00", "variance": 0.2})
        assert f["params"]["color"] == "#00ff00"
        assert f["params"]["variance"] == 0.2

    def test_volume_filter(self):
        proj = self._make_project_with_clip_on_track()
        f = add_filter(proj, 0, 0, "volume", {"gain": 0.5})
        assert f["params"]["gain"] == 0.5

    def test_speed_filter(self):
        proj = self._make_project_with_clip_on_track()
        f = add_filter(proj, 0, 0, "speed", {"speed": 2.0})
        assert f["params"]["speed"] == 2.0
