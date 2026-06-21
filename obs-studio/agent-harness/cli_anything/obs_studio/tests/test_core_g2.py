# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSources:
    def _make_project(self):
        return create_project()

    def test_add_source_video_capture(self):
        proj = self._make_project()
        src = add_source(proj, "video_capture", name="Camera")
        assert src["name"] == "Camera"
        assert src["type"] == "video_capture"
        assert len(proj["scenes"][0]["sources"]) == 1

    def test_add_source_all_types(self):
        proj = self._make_project()
        for stype in SOURCE_TYPES:
            src = add_source(proj, stype)
            assert src["type"] == stype
        assert len(proj["scenes"][0]["sources"]) == len(SOURCE_TYPES)

    def test_add_source_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Unknown source type"):
            add_source(proj, "nonexistent")

    def test_add_source_with_position(self):
        proj = self._make_project()
        src = add_source(proj, "image", position={"x": 100, "y": 200})
        assert src["position"]["x"] == 100.0
        assert src["position"]["y"] == 200.0

    def test_add_source_with_size(self):
        proj = self._make_project()
        src = add_source(proj, "color", size={"width": 800, "height": 600})
        assert src["size"]["width"] == 800
        assert src["size"]["height"] == 600

    def test_add_source_invalid_size(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="must be positive"):
            add_source(proj, "color", size={"width": 0, "height": 600})

    def test_add_source_with_settings(self):
        proj = self._make_project()
        src = add_source(proj, "browser", settings={"url": "https://example.com"})
        assert src["settings"]["url"] == "https://example.com"

    def test_add_source_unique_names(self):
        proj = self._make_project()
        s1 = add_source(proj, "text", name="Label")
        s2 = add_source(proj, "text", name="Label")
        assert s1["name"] != s2["name"]

    def test_remove_source(self):
        proj = self._make_project()
        add_source(proj, "image", name="BG")
        removed = remove_source(proj, 0)
        assert removed["name"] == "BG"
        assert len(proj["scenes"][0]["sources"]) == 0

    def test_remove_source_invalid_index(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="No source"):
            remove_source(proj, 0)

    def test_duplicate_source(self):
        proj = self._make_project()
        add_source(proj, "text", name="Title")
        dup = duplicate_source(proj, 0)
        assert "Copy" in dup["name"]
        assert len(proj["scenes"][0]["sources"]) == 2

    def test_set_source_property_visible(self):
        proj = self._make_project()
        add_source(proj, "image")
        set_source_property(proj, 0, "visible", "false")
        assert proj["scenes"][0]["sources"][0]["visible"] is False

    def test_set_source_property_opacity(self):
        proj = self._make_project()
        add_source(proj, "image")
        set_source_property(proj, 0, "opacity", 0.5)
        assert proj["scenes"][0]["sources"][0]["opacity"] == 0.5

    def test_set_source_property_invalid(self):
        proj = self._make_project()
        add_source(proj, "image")
        with pytest.raises(ValueError, match="Unknown source property"):
            set_source_property(proj, 0, "bogus", "val")

    def test_set_source_property_opacity_range(self):
        proj = self._make_project()
        add_source(proj, "image")
        with pytest.raises(ValueError, match="must be between"):
            set_source_property(proj, 0, "opacity", 2.0)

    def test_transform_source_position(self):
        proj = self._make_project()
        add_source(proj, "image")
        src = transform_source(proj, 0, position={"x": 100, "y": 200})
        assert src["position"]["x"] == 100.0

    def test_transform_source_size(self):
        proj = self._make_project()
        add_source(proj, "image")
        src = transform_source(proj, 0, size={"width": 640, "height": 480})
        assert src["size"]["width"] == 640

    def test_transform_source_crop(self):
        proj = self._make_project()
        add_source(proj, "image")
        src = transform_source(
            proj, 0, crop={"top": 10, "bottom": 20, "left": 5, "right": 5}
        )
        assert src["crop"]["top"] == 10

    def test_transform_source_rotation(self):
        proj = self._make_project()
        add_source(proj, "image")
        src = transform_source(proj, 0, rotation=45.0)
        assert src["rotation"] == 45.0

    def test_list_sources(self):
        proj = self._make_project()
        add_source(proj, "image", name="BG")
        add_source(proj, "text", name="Title")
        result = list_sources(proj)
        assert len(result) == 2

    def test_get_source(self):
        proj = self._make_project()
        add_source(proj, "image", name="Test")
        src = get_source(proj, 0)
        assert src["name"] == "Test"

    def test_source_default_properties(self):
        proj = self._make_project()
        src = add_source(proj, "color")
        assert src["visible"] is True
        assert src["locked"] is False
        assert src["opacity"] == 1.0
        assert src["rotation"] == 0
