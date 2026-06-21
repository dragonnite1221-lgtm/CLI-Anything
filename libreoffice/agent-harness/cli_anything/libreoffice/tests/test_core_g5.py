# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestStyles:
    def _make_doc(self):
        return create_document(doc_type="writer")

    def test_create_style(self):
        proj = self._make_doc()
        result = create_style(proj, "MyStyle", properties={"bold": True})
        assert result["name"] == "MyStyle"
        assert result["properties"]["bold"] is True

    def test_create_style_duplicate(self):
        proj = self._make_doc()
        create_style(proj, "S1")
        with pytest.raises(ValueError, match="already exists"):
            create_style(proj, "S1")

    def test_create_style_invalid_family(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Invalid style family"):
            create_style(proj, "S1", family="table")

    def test_create_style_invalid_property(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Unknown style properties"):
            create_style(proj, "S1", properties={"bogus": True})

    def test_modify_style(self):
        proj = self._make_doc()
        create_style(proj, "S1", properties={"bold": True})
        result = modify_style(proj, "S1", properties={"italic": True})
        assert result["properties"]["bold"] is True
        assert result["properties"]["italic"] is True

    def test_modify_nonexistent(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="not found"):
            modify_style(proj, "NoStyle")

    def test_remove_style(self):
        proj = self._make_doc()
        create_style(proj, "S1")
        removed = remove_style(proj, "S1")
        assert removed["name"] == "S1"
        assert "S1" not in proj["styles"]

    def test_list_styles(self):
        proj = self._make_doc()
        create_style(proj, "A")
        create_style(proj, "B")
        result = list_styles(proj)
        assert len(result) == 2

    def test_get_style(self):
        proj = self._make_doc()
        create_style(proj, "TestStyle", properties={"font_size": "14pt"})
        result = get_style(proj, "TestStyle")
        assert result["properties"]["font_size"] == "14pt"

    def test_apply_style(self):
        proj = self._make_doc()
        add_paragraph(proj, text="Hello")
        create_style(proj, "Bold", properties={"bold": True})
        result = apply_style(proj, "Bold", 0)
        assert result["style_applied"] == "Bold"
        assert proj["content"][0]["style"]["bold"] is True

    def test_apply_style_not_writer(self):
        proj = create_document(doc_type="calc")
        with pytest.raises(ValueError, match="only supported for Writer"):
            apply_style(proj, "S1", 0)

    def test_apply_nonexistent_style(self):
        proj = self._make_doc()
        add_paragraph(proj, text="Test")
        with pytest.raises(ValueError, match="not found"):
            apply_style(proj, "NoStyle", 0)
