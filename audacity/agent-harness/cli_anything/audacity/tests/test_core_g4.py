# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestLabels:
    def _make_project(self):
        return create_project()

    def test_add_label_point(self):
        proj = self._make_project()
        label = add_label(proj, 5.0, text="Intro")
        assert label["start"] == 5.0
        assert label["end"] == 5.0
        assert label["text"] == "Intro"

    def test_add_label_range(self):
        proj = self._make_project()
        label = add_label(proj, 5.0, 10.0, "Chorus")
        assert label["start"] == 5.0
        assert label["end"] == 10.0

    def test_add_label_invalid_start(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="start must be >= 0"):
            add_label(proj, -1.0)

    def test_add_label_invalid_range(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="end.*must be >= start"):
            add_label(proj, 10.0, 5.0)

    def test_remove_label(self):
        proj = self._make_project()
        add_label(proj, 1.0, text="Remove")
        removed = remove_label(proj, 0)
        assert removed["text"] == "Remove"
        assert len(proj["labels"]) == 0

    def test_remove_label_out_of_range(self):
        proj = self._make_project()
        with pytest.raises(IndexError):
            remove_label(proj, 0)

    def test_list_labels(self):
        proj = self._make_project()
        add_label(proj, 0.0, text="Start")
        add_label(proj, 5.0, 10.0, "Middle")
        add_label(proj, 15.0, text="End")
        labels = list_labels(proj)
        assert len(labels) == 3
        assert labels[0]["type"] == "point"
        assert labels[1]["type"] == "range"
        assert labels[1]["duration"] == 5.0


class TestSelection:
    def _make_project(self):
        return create_project()

    def test_set_selection(self):
        proj = self._make_project()
        result = set_selection(proj, 2.0, 8.0)
        assert result["start"] == 2.0
        assert result["end"] == 8.0

    def test_set_selection_invalid(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="start must be >= 0"):
            set_selection(proj, -1.0, 5.0)
        with pytest.raises(ValueError, match="end.*must be >= start"):
            set_selection(proj, 10.0, 5.0)

    def test_select_all_empty(self):
        proj = self._make_project()
        result = select_all(proj)
        assert result["end"] == 0.0

    def test_select_all_with_clips(self):
        proj = self._make_project()
        add_track(proj, name="T1")
        add_clip(proj, 0, "/fake/a.wav", start_time=0.0, end_time=30.0)
        result = select_all(proj)
        assert result["start"] == 0.0
        assert result["end"] == 30.0

    def test_select_none(self):
        proj = self._make_project()
        set_selection(proj, 1.0, 5.0)
        result = select_none(proj)
        assert result["start"] == 0.0
        assert result["end"] == 0.0

    def test_get_selection(self):
        proj = self._make_project()
        set_selection(proj, 3.0, 7.0)
        result = get_selection(proj)
        assert result["start"] == 3.0
        assert result["end"] == 7.0
        assert result["duration"] == 4.0
        assert result["has_selection"] is True

    def test_get_selection_empty(self):
        proj = self._make_project()
        result = get_selection(proj)
        assert result["has_selection"] is False
