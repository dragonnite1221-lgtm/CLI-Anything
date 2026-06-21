# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPaths:
    def _make_doc_with_shapes(self):
        proj = create_document()
        add_rect(proj, name="Rect1")
        add_circle(proj, name="Circle1")
        return proj

    def test_union(self):
        proj = self._make_doc_with_shapes()
        result = path_union(proj, 0, 1)
        assert result["type"] == "path"
        assert result["boolean_operation"]["type"] == "union"
        assert len(proj["objects"]) == 1

    def test_intersection(self):
        proj = self._make_doc_with_shapes()
        result = path_intersection(proj, 0, 1)
        assert result["boolean_operation"]["type"] == "intersection"

    def test_difference(self):
        proj = self._make_doc_with_shapes()
        result = path_difference(proj, 0, 1)
        assert result["boolean_operation"]["type"] == "difference"

    def test_exclusion(self):
        proj = self._make_doc_with_shapes()
        result = path_exclusion(proj, 0, 1)
        assert result["boolean_operation"]["type"] == "exclusion"

    def test_boolean_same_object_fails(self):
        proj = self._make_doc_with_shapes()
        with pytest.raises(ValueError, match="same object"):
            path_union(proj, 0, 0)

    def test_boolean_invalid_index(self):
        proj = self._make_doc_with_shapes()
        with pytest.raises(IndexError):
            path_union(proj, 0, 5)

    def test_convert_rect_to_path(self):
        proj = create_document()
        add_rect(proj, x=10, y=10, width=100, height=50)
        result = convert_to_path(proj, 0)
        assert result["type"] == "path"
        assert "M" in result["d"]
        assert result["original_type"] == "rect"

    def test_convert_circle_to_path(self):
        proj = create_document()
        add_circle(proj, cx=50, cy=50, r=25)
        result = convert_to_path(proj, 0)
        assert result["type"] == "path"
        assert "A" in result["d"]

    def test_convert_ellipse_to_path(self):
        proj = create_document()
        add_ellipse(proj)
        result = convert_to_path(proj, 0)
        assert result["type"] == "path"

    def test_convert_path_is_noop(self):
        proj = create_document()
        add_path(proj, d="M 0,0 L 100,100")
        result = convert_to_path(proj, 0)
        assert result["d"] == "M 0,0 L 100,100"

    def test_list_path_operations(self):
        ops = list_path_operations()
        assert len(ops) >= 4
        names = [o["name"] for o in ops]
        assert "union" in names
        assert "difference" in names

    def test_convert_line_to_path(self):
        proj = create_document()
        add_line(proj, x1=0, y1=0, x2=100, y2=100)
        result = convert_to_path(proj, 0)
        assert result["type"] == "path"
        assert "M" in result["d"]

    def test_convert_polygon_to_path(self):
        proj = create_document()
        add_polygon(proj, points="50,0 100,100 0,100")
        result = convert_to_path(proj, 0)
        assert result["type"] == "path"
        assert "Z" in result["d"]
