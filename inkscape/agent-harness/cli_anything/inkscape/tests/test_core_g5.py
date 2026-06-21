# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestStyles:
    def _make_doc_with_rect(self):
        proj = create_document()
        add_rect(proj)
        return proj

    def test_set_fill(self):
        proj = self._make_doc_with_rect()
        set_fill(proj, 0, "#ff0000")
        style = parse_style(proj["objects"][0]["style"])
        assert style["fill"] == "#ff0000"

    def test_set_stroke(self):
        proj = self._make_doc_with_rect()
        set_stroke(proj, 0, "#00ff00", width=3)
        style = parse_style(proj["objects"][0]["style"])
        assert style["stroke"] == "#00ff00"
        assert style["stroke-width"] == "3"

    def test_set_stroke_negative_width(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="non-negative"):
            set_stroke(proj, 0, "#000", width=-1)

    def test_set_opacity(self):
        proj = self._make_doc_with_rect()
        set_opacity(proj, 0, 0.5)
        style = parse_style(proj["objects"][0]["style"])
        assert style["opacity"] == "0.5"

    def test_set_opacity_invalid(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="0.0-1.0"):
            set_opacity(proj, 0, 1.5)

    def test_set_style_arbitrary(self):
        proj = self._make_doc_with_rect()
        set_style(proj, 0, "stroke-linecap", "round")
        style = parse_style(proj["objects"][0]["style"])
        assert style["stroke-linecap"] == "round"

    def test_set_style_invalid_property(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="Unknown style property"):
            set_style(proj, 0, "bogus", "value")

    def test_set_style_invalid_choice(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="Invalid value"):
            set_style(proj, 0, "stroke-linecap", "diamond")

    def test_get_object_style(self):
        proj = self._make_doc_with_rect()
        set_fill(proj, 0, "#ff0000")
        style = get_object_style(proj, 0)
        assert "fill" in style

    def test_list_style_properties(self):
        props = list_style_properties()
        assert len(props) > 0
        names = [p["name"] for p in props]
        assert "fill" in names
        assert "stroke" in names
        assert "opacity" in names

    def test_set_fill_opacity(self):
        proj = self._make_doc_with_rect()
        set_style(proj, 0, "fill-opacity", "0.5")
        style = parse_style(proj["objects"][0]["style"])
        assert style["fill-opacity"] == "0.5"

    def test_set_fill_opacity_invalid(self):
        proj = self._make_doc_with_rect()
        with pytest.raises(ValueError, match="0.0-1.0"):
            set_style(proj, 0, "fill-opacity", "2.0")
