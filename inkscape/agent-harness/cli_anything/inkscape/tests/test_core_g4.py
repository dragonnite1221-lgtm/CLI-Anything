# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestText:
    def _make_doc(self):
        return create_document()

    def test_add_text(self):
        proj = self._make_doc()
        obj = add_text(proj, text="Hello World", x=100, y=200)
        assert obj["type"] == "text"
        assert obj["text"] == "Hello World"
        assert obj["x"] == 100

    def test_add_text_with_box(self):
        proj = self._make_doc()
        obj = add_text(
            proj, text="Wrapped text", x=10, y=20, box_width=200, box_height=80
        )
        assert obj["box_width"] == 200
        assert obj["box_height"] == 80

    def test_add_text_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="cannot be empty"):
            add_text(proj, text="")

    def test_add_text_invalid_font_size(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="must be positive"):
            add_text(proj, text="Hi", font_size=0)

    def test_set_text_content(self):
        proj = self._make_doc()
        add_text(proj, text="Old")
        set_text_property(proj, 0, "text", "New")
        assert proj["objects"][0]["text"] == "New"

    def test_set_font_family(self):
        proj = self._make_doc()
        add_text(proj, text="Hi")
        set_text_property(proj, 0, "font-family", "serif")
        assert proj["objects"][0]["font_family"] == "serif"

    def test_set_font_size(self):
        proj = self._make_doc()
        add_text(proj, text="Hi")
        set_text_property(proj, 0, "font-size", "48")
        assert proj["objects"][0]["font_size"] == 48.0

    def test_set_box_width(self):
        proj = self._make_doc()
        add_text(proj, text="Hi")
        set_text_property(proj, 0, "box-width", "220")
        assert proj["objects"][0]["box_width"] == 220.0

    def test_set_invalid_font_weight(self):
        proj = self._make_doc()
        add_text(proj, text="Hi")
        with pytest.raises(ValueError, match="Invalid font-weight"):
            set_text_property(proj, 0, "font-weight", "extra-heavy")

    def test_set_invalid_property(self):
        proj = self._make_doc()
        add_text(proj, text="Hi")
        with pytest.raises(ValueError, match="Unknown text property"):
            set_text_property(proj, 0, "bogus", "value")

    def test_set_on_non_text(self):
        proj = self._make_doc()
        add_rect(proj)
        with pytest.raises(ValueError, match="not a text element"):
            set_text_property(proj, 0, "text", "Hi")

    def test_list_text_objects(self):
        proj = self._make_doc()
        add_text(proj, text="A")
        add_rect(proj)
        add_text(proj, text="B")
        result = list_text_objects(proj)
        assert len(result) == 2

    def test_text_style_rebuilt(self):
        proj = self._make_doc()
        add_text(proj, text="Hi", fill="#ff0000")
        set_text_property(proj, 0, "font-size", "48")
        style = proj["objects"][0]["style"]
        assert "48" in style and "px" in style
        assert "#ff0000" in style

    def test_layout_text_lines_wraps(self):
        proj = self._make_doc()
        obj = add_text(
            proj,
            text="Real capture plus Veo cold open plus Gemini score",
            box_width=120,
            box_height=90,
            font_size=20,
        )
        lines = layout_text_lines(obj)
        assert len(lines) > 1
