# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTransforms:
    def _make_doc_with_rect(self):
        proj = create_document()
        add_rect(proj)
        return proj

    def test_translate(self):
        proj = self._make_doc_with_rect()
        translate(proj, 0, 100, 50)
        t = get_transform(proj, 0)
        assert "translate(100, 50)" in t["raw"]

    def test_rotate(self):
        proj = self._make_doc_with_rect()
        rotate(proj, 0, 45)
        t = get_transform(proj, 0)
        assert "rotate(45)" in t["raw"]

    def test_rotate_with_center(self):
        proj = self._make_doc_with_rect()
        rotate(proj, 0, 90, cx=50, cy=50)
        t = get_transform(proj, 0)
        assert "rotate(90, 50, 50)" in t["raw"]

    def test_scale(self):
        proj = self._make_doc_with_rect()
        scale(proj, 0, 2)
        t = get_transform(proj, 0)
        assert "scale(2)" in t["raw"]

    def test_scale_non_uniform(self):
        proj = self._make_doc_with_rect()
        scale(proj, 0, 2, 3)
        t = get_transform(proj, 0)
        assert "scale(2, 3)" in t["raw"]

    def test_scale_zero_raises(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="non-zero"):
            scale(proj, 0, 0)

    def test_skew_x(self):
        proj = self._make_doc_with_rect()
        skew_x(proj, 0, 30)
        t = get_transform(proj, 0)
        assert "skewX(30)" in t["raw"]

    def test_skew_y(self):
        proj = self._make_doc_with_rect()
        skew_y(proj, 0, 15)
        t = get_transform(proj, 0)
        assert "skewY(15)" in t["raw"]

    def test_compound_transforms(self):
        proj = self._make_doc_with_rect()
        translate(proj, 0, 10, 20)
        rotate(proj, 0, 45)
        t = get_transform(proj, 0)
        assert "translate" in t["raw"]
        assert "rotate" in t["raw"]
        assert len(t["operations"]) == 2

    def test_set_transform(self):
        proj = self._make_doc_with_rect()
        set_transform(proj, 0, "matrix(1,0,0,1,10,20)")
        t = get_transform(proj, 0)
        assert "matrix" in t["raw"]

    def test_clear_transform(self):
        proj = self._make_doc_with_rect()
        translate(proj, 0, 100, 100)
        result = clear_transform(proj, 0)
        assert result["new_transform"] == ""
        assert proj["objects"][0]["transform"] == ""

    def test_parse_transform_string(self):
        ops = parse_transform_string("translate(10, 20) rotate(45) scale(2, 3)")
        assert len(ops) == 3
        assert ops[0] == ("translate", [10.0, 20.0])
        assert ops[1] == ("rotate", [45.0])
        assert ops[2] == ("scale", [2.0, 3.0])

    def test_parse_empty_transform(self):
        assert parse_transform_string("") == []
        assert parse_transform_string(None) == []

    def test_serialize_transform_string(self):
        ops = [("translate", [10.0, 20.0]), ("rotate", [45.0])]
        result = serialize_transform_string(ops)
        assert "translate(10, 20)" in result
        assert "rotate(45)" in result

    def test_serialize_empty(self):
        assert serialize_transform_string([]) == ""
