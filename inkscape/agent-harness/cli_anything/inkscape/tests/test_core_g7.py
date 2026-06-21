# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestLayers:
    def _make_doc(self):
        return create_document()

    def test_add_layer(self):
        proj = self._make_doc()
        layer = add_layer(proj, name="Layer 2")
        assert layer["name"] == "Layer 2"
        assert len(proj["layers"]) == 2

    def test_add_layer_unique_names(self):
        proj = self._make_doc()
        l1 = add_layer(proj, name="Layer 1")
        # "Layer 1" already exists as default
        assert l1["name"] == "Layer 1 2"

    def test_add_layer_invalid_opacity(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="0.0-1.0"):
            add_layer(proj, opacity=1.5)

    def test_remove_layer(self):
        proj = self._make_doc()
        add_layer(proj, name="Second")
        removed = remove_layer(proj, 1)
        assert removed["name"] == "Second"
        assert len(proj["layers"]) == 1

    def test_remove_last_layer_fails(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Cannot remove the last"):
            remove_layer(proj, 0)

    def test_move_to_layer(self):
        proj = self._make_doc()
        add_rect(proj, name="Shape")
        add_layer(proj, name="Layer 2")
        result = move_to_layer(proj, 0, 1)
        assert proj["objects"][0]["layer"] == proj["layers"][1]["id"]

    def test_set_layer_property_visible(self):
        proj = self._make_doc()
        set_layer_property(proj, 0, "visible", "false")
        assert proj["layers"][0]["visible"] is False

    def test_set_layer_property_locked(self):
        proj = self._make_doc()
        set_layer_property(proj, 0, "locked", "true")
        assert proj["layers"][0]["locked"] is True

    def test_set_layer_property_opacity(self):
        proj = self._make_doc()
        set_layer_property(proj, 0, "opacity", "0.5")
        assert proj["layers"][0]["opacity"] == 0.5

    def test_set_layer_property_name(self):
        proj = self._make_doc()
        set_layer_property(proj, 0, "name", "Renamed")
        assert proj["layers"][0]["name"] == "Renamed"

    def test_set_layer_property_invalid(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Unknown layer property"):
            set_layer_property(proj, 0, "bogus", "value")

    def test_list_layers(self):
        proj = self._make_doc()
        add_layer(proj, name="Second")
        result = list_layers(proj)
        assert len(result) == 2

    def test_reorder_layers(self):
        proj = self._make_doc()
        add_layer(proj, name="Second")
        add_layer(proj, name="Third")
        reorder_layers(proj, 0, 2)
        assert proj["layers"][2]["name"] == "Layer 1"
        assert proj["layers"][0]["name"] == "Second"

    def test_get_layer(self):
        proj = self._make_doc()
        add_rect(proj, name="Shape")
        layer = get_layer(proj, 0)
        assert layer["name"] == "Layer 1"
        assert len(layer["objects"]) == 1

    def test_remove_layer_moves_objects(self):
        proj = self._make_doc()
        add_layer(proj, name="Second")
        # Add object to second layer
        obj = add_rect(proj, name="Shape", layer=proj["layers"][1]["id"])
        # Remove second layer
        remove_layer(proj, 1)
        # Object should be moved to first layer
        assert obj["id"] in proj["layers"][0]["objects"]
