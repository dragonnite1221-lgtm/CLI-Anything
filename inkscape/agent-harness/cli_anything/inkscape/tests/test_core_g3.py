# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestShapes:
    def _make_doc(self):
        return create_document()

    def test_add_rect(self):
        proj = self._make_doc()
        obj = add_rect(proj, x=10, y=20, width=200, height=100)
        assert obj["type"] == "rect"
        assert obj["x"] == 10
        assert obj["width"] == 200
        assert len(proj["objects"]) == 1

    def test_add_rect_invalid_dimensions(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="must be positive"):
            add_rect(proj, width=0, height=100)

    def test_add_circle(self):
        proj = self._make_doc()
        obj = add_circle(proj, cx=100, cy=100, r=50)
        assert obj["type"] == "circle"
        assert obj["r"] == 50

    def test_add_circle_invalid_radius(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="must be positive"):
            add_circle(proj, r=-5)

    def test_add_ellipse(self):
        proj = self._make_doc()
        obj = add_ellipse(proj, cx=50, cy=50, rx=100, ry=50)
        assert obj["type"] == "ellipse"
        assert obj["rx"] == 100
        assert obj["ry"] == 50

    def test_add_ellipse_invalid(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="must be positive"):
            add_ellipse(proj, rx=-1, ry=50)

    def test_add_line(self):
        proj = self._make_doc()
        obj = add_line(proj, x1=0, y1=0, x2=100, y2=100)
        assert obj["type"] == "line"
        assert obj["x2"] == 100

    def test_add_polygon(self):
        proj = self._make_doc()
        obj = add_polygon(proj, points="50,0 100,100 0,100")
        assert obj["type"] == "polygon"
        assert "50,0" in obj["points"]

    def test_add_polygon_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="at least one point"):
            add_polygon(proj, points="")

    def test_add_path(self):
        proj = self._make_doc()
        obj = add_path(proj, d="M 0,0 L 100,0 L 100,100 Z")
        assert obj["type"] == "path"
        assert "M 0,0" in obj["d"]

    def test_add_path_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="cannot be empty"):
            add_path(proj, d="")

    def test_add_star(self):
        proj = self._make_doc()
        obj = add_star(proj, cx=100, cy=100, points_count=5, outer_r=50, inner_r=25)
        assert obj["type"] == "star"
        assert obj["points_count"] == 5
        assert "d" in obj

    def test_add_star_invalid_points(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="at least 3"):
            add_star(proj, points_count=2)

    def test_add_star_invalid_radius(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="must be positive"):
            add_star(proj, outer_r=-1, inner_r=25)

    def test_remove_object(self):
        proj = self._make_doc()
        add_rect(proj, name="A")
        add_circle(proj, name="B")
        removed = remove_object(proj, 0)
        assert removed["name"] == "A"
        assert len(proj["objects"]) == 1

    def test_remove_object_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="No objects"):
            remove_object(proj, 0)

    def test_remove_object_invalid_index(self):
        proj = self._make_doc()
        add_rect(proj)
        with pytest.raises(IndexError):
            remove_object(proj, 5)

    def test_duplicate_object(self):
        proj = self._make_doc()
        add_rect(proj, name="Original")
        dup = duplicate_object(proj, 0)
        assert "copy" in dup["name"]
        assert len(proj["objects"]) == 2
        assert dup["id"] != proj["objects"][0]["id"]

    def test_list_objects(self):
        proj = self._make_doc()
        add_rect(proj, name="R")
        add_circle(proj, name="C")
        result = list_objects(proj)
        assert len(result) == 2

    def test_get_object(self):
        proj = self._make_doc()
        add_rect(proj, name="Test")
        obj = get_object(proj, 0)
        assert obj["name"] == "Test"

    def test_unique_ids(self):
        proj = self._make_doc()
        a = add_rect(proj, name="A")
        b = add_rect(proj, name="B")
        assert a["id"] != b["id"]

    def test_object_added_to_layer(self):
        proj = self._make_doc()
        obj = add_rect(proj)
        assert obj["id"] in proj["layers"][0]["objects"]

    def test_all_shape_types_registered(self):
        expected = {
            "rect",
            "circle",
            "ellipse",
            "line",
            "polygon",
            "polyline",
            "path",
            "text",
            "star",
            "image",
        }
        assert expected.issubset(set(SHAPE_TYPES.keys()))

    def test_add_rect_with_custom_style(self):
        proj = self._make_doc()
        obj = add_rect(proj, style="fill:#ff0000;stroke:none")
        assert "fill:#ff0000" in obj["style"]

    def test_add_rect_rounded_corners(self):
        proj = self._make_doc()
        obj = add_rect(proj, rx=10, ry=10)
        assert obj["rx"] == 10
        assert obj["ry"] == 10
