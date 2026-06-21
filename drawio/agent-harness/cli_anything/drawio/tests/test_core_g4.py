# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestShapes:
    def test_add_shape(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle", 10, 20, 120, 60, "Hello")
        assert result["action"] == "add_shape"
        assert result["label"] == "Hello"
        assert result["id"] is not None

    def test_add_shape_no_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project is open"):
            shapes_mod.add_shape(s, "rectangle")

    def test_list_shapes(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", label="A")
        shapes_mod.add_shape(s, "ellipse", label="B")
        result = shapes_mod.list_shapes(s)
        assert len(result) == 2

    def test_remove_shape(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle", label="ToRemove")
        cell_id = result["id"]
        shapes_mod.remove_shape(s, cell_id)
        assert len(shapes_mod.list_shapes(s)) == 0

    def test_remove_shape_not_found(self):
        s = Session()
        proj_mod.new_project(s)
        with pytest.raises(ValueError, match="Shape not found"):
            shapes_mod.remove_shape(s, "nonexistent")

    def test_update_label(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle", label="Old")
        shapes_mod.update_label(s, result["id"], "New")
        shapes = shapes_mod.list_shapes(s)
        assert shapes[0]["value"] == "New"

    def test_move_shape(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle", 10, 20, 100, 50)
        shapes_mod.move_shape(s, result["id"], 300, 400)
        info = shapes_mod.get_shape_info(s, result["id"])
        assert info["x"] == 300.0
        assert info["y"] == 400.0

    def test_resize_shape(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle", 10, 20, 100, 50)
        shapes_mod.resize_shape(s, result["id"], 200, 150)
        info = shapes_mod.get_shape_info(s, result["id"])
        assert info["width"] == 200.0
        assert info["height"] == 150.0

    def test_set_style(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "rectangle")
        shapes_mod.set_style(s, result["id"], "fillColor", "#ff0000")
        info = shapes_mod.get_shape_info(s, result["id"])
        assert info["style_parsed"]["fillColor"] == "#ff0000"

    def test_get_shape_info(self):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, "ellipse", 50, 60, 80, 80, "Circle")
        info = shapes_mod.get_shape_info(s, result["id"])
        assert info["value"] == "Circle"
        assert info["type"] == "vertex"
        assert "style_parsed" in info

    def test_list_shape_types(self):
        types = shapes_mod.list_shape_types()
        assert "rectangle" in types
        assert "ellipse" in types
        assert "diamond" in types

    @pytest.mark.parametrize(
        "shape_type",
        [
            "rectangle",
            "rounded",
            "ellipse",
            "diamond",
            "triangle",
            "hexagon",
            "cylinder",
            "cloud",
            "parallelogram",
            "process",
            "document",
            "callout",
            "note",
            "actor",
            "text",
        ],
    )
    def test_all_shape_types_via_module(self, shape_type):
        s = Session()
        proj_mod.new_project(s)
        result = shapes_mod.add_shape(s, shape_type, label=shape_type)
        assert result["shape_type"] == shape_type

    def test_undo_add_shape(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", label="Test")
        assert len(shapes_mod.list_shapes(s)) == 1
        s.undo()
        assert len(shapes_mod.list_shapes(s)) == 0
