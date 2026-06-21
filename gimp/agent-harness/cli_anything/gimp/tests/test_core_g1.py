# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestLayers:
    def _make_project(self):
        return create_project()

    def test_add_layer(self):
        proj = self._make_project()
        layer = add_layer(proj, name="Test", layer_type="image")
        assert layer["name"] == "Test"
        assert layer["type"] == "image"
        assert len(proj["layers"]) == 1

    def test_add_multiple_layers(self):
        proj = self._make_project()
        add_layer(proj, name="Bottom")
        add_layer(proj, name="Top")
        assert len(proj["layers"]) == 2
        assert proj["layers"][0]["name"] == "Top"  # Top of stack

    def test_add_layer_with_position(self):
        proj = self._make_project()
        add_layer(proj, name="First")
        add_layer(proj, name="Second", position=1)
        assert proj["layers"][1]["name"] == "Second"

    def test_add_layer_invalid_mode(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid blend mode"):
            add_layer(proj, blend_mode="invalid")

    def test_add_layer_invalid_opacity(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Opacity"):
            add_layer(proj, opacity=1.5)

    def test_remove_layer(self):
        proj = self._make_project()
        add_layer(proj, name="A")
        add_layer(proj, name="B")
        removed = remove_layer(proj, 0)
        assert removed["name"] == "B"
        assert len(proj["layers"]) == 1

    def test_remove_layer_invalid_index(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="No layers"):
            remove_layer(proj, 0)

    def test_duplicate_layer(self):
        proj = self._make_project()
        add_layer(proj, name="Original")
        dup = duplicate_layer(proj, 0)
        assert dup["name"] == "Original copy"
        assert len(proj["layers"]) == 2

    def test_move_layer(self):
        proj = self._make_project()
        add_layer(proj, name="A")
        add_layer(proj, name="B")
        add_layer(proj, name="C")
        move_layer(proj, 0, 2)
        assert proj["layers"][2]["name"] == "C"

    def test_set_property_opacity(self):
        proj = self._make_project()
        add_layer(proj, name="Test")
        set_layer_property(proj, 0, "opacity", 0.5)
        assert proj["layers"][0]["opacity"] == 0.5

    def test_set_property_visible(self):
        proj = self._make_project()
        add_layer(proj, name="Test")
        set_layer_property(proj, 0, "visible", "false")
        assert proj["layers"][0]["visible"] is False

    def test_set_property_name(self):
        proj = self._make_project()
        add_layer(proj, name="Old")
        set_layer_property(proj, 0, "name", "New")
        assert proj["layers"][0]["name"] == "New"

    def test_set_property_invalid(self):
        proj = self._make_project()
        add_layer(proj, name="Test")
        with pytest.raises(ValueError, match="Unknown property"):
            set_layer_property(proj, 0, "bogus", "value")

    def test_get_layer(self):
        proj = self._make_project()
        add_layer(proj, name="Test")
        layer = get_layer(proj, 0)
        assert layer["name"] == "Test"

    def test_list_layers(self):
        proj = self._make_project()
        add_layer(proj, name="A")
        add_layer(proj, name="B")
        result = list_layers(proj)
        assert len(result) == 2
        assert result[0]["name"] == "B"

    def test_layer_ids_unique(self):
        proj = self._make_project()
        l1 = add_layer(proj, name="A")
        l2 = add_layer(proj, name="B")
        assert l1["id"] != l2["id"]

    def test_solid_layer(self):
        proj = self._make_project()
        layer = add_layer(proj, name="Red", layer_type="solid", fill="#ff0000")
        assert layer["type"] == "solid"
        assert layer["fill"] == "#ff0000"

    def test_text_layer(self):
        proj = self._make_project()
        layer = add_layer(proj, name="Title", layer_type="text")
        assert layer["type"] == "text"
        assert "text" in layer
        assert "font_size" in layer

    def test_layer_can_store_draw_ops(self):
        proj = self._make_project()
        layer = add_layer(proj, name="Overlay", layer_type="image")
        layer.setdefault("draw_ops", []).append({"type": "text", "text": "Hello"})
        assert layer["type"] == "image"
        assert layer["draw_ops"][0]["type"] == "text"
