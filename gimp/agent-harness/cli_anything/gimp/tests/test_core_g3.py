# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCanvas:
    def _make_project(self):
        return create_project(width=800, height=600)

    def test_resize_canvas(self):
        proj = self._make_project()
        result = resize_canvas(proj, 1000, 800)
        assert proj["canvas"]["width"] == 1000
        assert proj["canvas"]["height"] == 800
        assert "old_size" in result

    def test_resize_canvas_with_anchor(self):
        proj = self._make_project()
        add_layer(proj, name="Test")
        resize_canvas(proj, 1000, 800, anchor="top-left")
        assert proj["layers"][0]["offset_x"] == 0
        assert proj["layers"][0]["offset_y"] == 0

    def test_resize_canvas_invalid_size(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="must be positive"):
            resize_canvas(proj, 0, 100)

    def test_scale_canvas(self):
        proj = self._make_project()
        add_layer(proj, name="Test", width=800, height=600)
        result = scale_canvas(proj, 400, 300)
        assert proj["canvas"]["width"] == 400
        assert proj["canvas"]["height"] == 300
        assert proj["layers"][0]["width"] == 400
        assert proj["layers"][0]["height"] == 300

    def test_crop_canvas(self):
        proj = self._make_project()
        result = crop_canvas(proj, 100, 100, 500, 400)
        assert proj["canvas"]["width"] == 400
        assert proj["canvas"]["height"] == 300

    def test_crop_canvas_out_of_bounds(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="exceeds canvas"):
            crop_canvas(proj, 0, 0, 1000, 1000)

    def test_crop_canvas_invalid_region(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid crop"):
            crop_canvas(proj, 500, 500, 100, 100)

    def test_set_mode(self):
        proj = self._make_project()
        result = set_mode(proj, "RGBA")
        assert proj["canvas"]["color_mode"] == "RGBA"
        assert result["old_mode"] == "RGB"

    def test_set_mode_invalid(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid color mode"):
            set_mode(proj, "XYZ")

    def test_set_dpi(self):
        proj = self._make_project()
        result = set_dpi(proj, 300)
        assert proj["canvas"]["dpi"] == 300

    def test_get_canvas_info(self):
        proj = self._make_project()
        info = get_canvas_info(proj)
        assert info["width"] == 800
        assert info["height"] == 600
        assert "megapixels" in info
