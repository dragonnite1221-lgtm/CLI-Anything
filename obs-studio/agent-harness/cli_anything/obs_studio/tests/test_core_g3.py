# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFilters:
    def _make_project_with_source(self):
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")
        return proj

    def test_add_filter(self):
        proj = self._make_project_with_source()
        filt = add_filter(proj, "color_correction", 0)
        assert filt["type"] == "color_correction"
        assert filt["enabled"] is True
        assert len(proj["scenes"][0]["sources"][0]["filters"]) == 1

    def test_add_filter_with_params(self):
        proj = self._make_project_with_source()
        filt = add_filter(proj, "color_correction", 0, params={"brightness": 0.5})
        assert filt["params"]["brightness"] == 0.5

    def test_add_filter_invalid_type(self):
        proj = self._make_project_with_source()
        with pytest.raises(ValueError, match="Unknown filter type"):
            add_filter(proj, "nonexistent", 0)

    def test_add_filter_invalid_param(self):
        proj = self._make_project_with_source()
        with pytest.raises(ValueError, match="Unknown parameters"):
            add_filter(proj, "color_correction", 0, params={"bogus": 1})

    def test_add_filter_param_out_of_range(self):
        proj = self._make_project_with_source()
        with pytest.raises(ValueError, match="must be between"):
            add_filter(proj, "color_correction", 0, params={"brightness": 5.0})

    def test_add_chroma_key(self):
        proj = self._make_project_with_source()
        filt = add_filter(proj, "chroma_key", 0, params={"similarity": 500})
        assert filt["params"]["similarity"] == 500

    def test_add_noise_suppress(self):
        proj = self._make_project_with_source()
        filt = add_filter(proj, "noise_suppress", 0)
        assert filt["params"]["method"] == "rnnoise"

    def test_remove_filter(self):
        proj = self._make_project_with_source()
        add_filter(proj, "gain", 0)
        removed = remove_filter(proj, 0, 0)
        assert removed["type"] == "gain"
        assert len(proj["scenes"][0]["sources"][0]["filters"]) == 0

    def test_set_filter_param(self):
        proj = self._make_project_with_source()
        add_filter(proj, "gain", 0, params={"db": 0.0})
        set_filter_param(proj, 0, "db", 5.0, 0)
        assert proj["scenes"][0]["sources"][0]["filters"][0]["params"]["db"] == 5.0

    def test_set_filter_param_invalid(self):
        proj = self._make_project_with_source()
        add_filter(proj, "gain", 0)
        with pytest.raises(ValueError, match="Unknown parameter"):
            set_filter_param(proj, 0, "bogus", 1.0, 0)

    def test_list_filters(self):
        proj = self._make_project_with_source()
        add_filter(proj, "gain", 0)
        add_filter(proj, "compressor", 0)
        result = list_filters(proj, 0)
        assert len(result) == 2

    def test_list_available_filters(self):
        result = list_available_filters()
        assert len(result) == len(FILTER_TYPES)
        names = [f["name"] for f in result]
        assert "color_correction" in names
        assert "chroma_key" in names

    def test_list_available_filters_by_category(self):
        audio = list_available_filters(category="audio")
        assert all(f["category"] == "audio" for f in audio)
        assert len(audio) >= 4

    def test_all_filter_types_have_params(self):
        for name, spec in FILTER_TYPES.items():
            assert "params" in spec, f"Filter '{name}' missing params"
            assert "label" in spec, f"Filter '{name}' missing label"
            assert "category" in spec, f"Filter '{name}' missing category"
