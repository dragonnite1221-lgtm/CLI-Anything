# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCrop:
    def test_default_crop(self):
        s = Session()
        s.new_project()
        crop = tl_mod.get_crop(s)
        assert crop == {"x": 0, "y": 0, "width": 1, "height": 1}

    def test_set_crop(self):
        s = Session()
        s.new_project()
        result = tl_mod.set_crop(s, 0.1, 0.1, 0.8, 0.8)
        assert result["x"] == 0.1
        assert result["width"] == 0.8

    def test_invalid_crop(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            tl_mod.set_crop(s, 0, 0, 1.5, 1)

    def test_crop_out_of_bounds(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError, match="beyond frame"):
            tl_mod.set_crop(s, 0.5, 0.5, 0.6, 0.6)

    # ── Extra tests from auto version ──────────────────────────────────

    def test_set_crop_overflow_x(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            tl_mod.set_crop(s, 0.5, 0.0, 0.6, 1.0)

    def test_set_crop_overflow_y(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            tl_mod.set_crop(s, 0.0, 0.5, 1.0, 0.6)

    def test_set_crop_negative_raises(self):
        s = Session()
        s.new_project()
        with pytest.raises(ValueError):
            tl_mod.set_crop(s, -0.1, 0.0, 1.0, 1.0)

    def test_set_crop_calls_checkpoint(self):
        s = Session()
        s.new_project()
        initial = len(s._undo_stack)
        tl_mod.set_crop(s, 0.0, 0.0, 0.5, 0.5)
        assert len(s._undo_stack) > initial

    def test_crop_full_frame_valid(self):
        s = Session()
        s.new_project()
        crop = tl_mod.set_crop(s, 0.0, 0.0, 1.0, 1.0)
        assert crop["x"] == 0.0


class TestAnnotation:
    def test_add_text_annotation(self):
        s = Session()
        s.new_project()
        result = tl_mod.add_text_annotation(s, 1000, 3000, "Hello World")
        assert result["type"] == "text"
        assert result["textContent"] == "Hello World"

    def test_list_and_remove(self):
        s = Session()
        s.new_project()
        a = tl_mod.add_text_annotation(s, 1000, 3000, "Test")
        assert len(tl_mod.list_annotations(s)) == 1
        tl_mod.remove_annotation(s, a["id"])
        assert len(tl_mod.list_annotations(s)) == 0

    # ── Extra tests from auto version ──────────────────────────────────

    def test_add_annotation_position(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_text_annotation(s, 0, 2000, "Positioned", x=0.25, y=0.75)
        assert region["position"]["x"] == 0.25
        assert region["position"]["y"] == 0.75

    def test_list_annotations_sorted(self):
        s = Session()
        s.new_project()
        tl_mod.add_text_annotation(s, 5000, 8000, "Later")
        tl_mod.add_text_annotation(s, 1000, 3000, "Earlier")
        regions = tl_mod.list_annotations(s)
        starts = [r["startMs"] for r in regions]
        assert starts == sorted(starts)

    def test_update_annotation_text(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_text_annotation(s, 0, 2000, "original")
        tl_mod.update_annotation(s, region["id"], text_content="updated")
        regions = tl_mod.list_annotations(s)
        assert regions[0]["textContent"] == "updated"

    def test_update_annotation_nonexistent(self):
        s = Session()
        s.new_project()
        with pytest.raises((ValueError, KeyError)):
            tl_mod.update_annotation(s, "fake-id", text_content="x")

    def test_annotation_style_fields(self):
        s = Session()
        s.new_project()
        region = tl_mod.add_text_annotation(
            s, 0, 1000, "Styled", color="#ff0000", font_size=32
        )
        assert region["style"]["color"] == "#ff0000"
        assert region["style"]["fontSize"] == 32
