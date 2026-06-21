# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestWriter:
    def _make_doc(self):
        return create_document(doc_type="writer")

    def test_add_paragraph(self):
        proj = self._make_doc()
        item = add_paragraph(proj, text="Hello world")
        assert item["type"] == "paragraph"
        assert item["text"] == "Hello world"
        assert len(proj["content"]) == 1

    def test_add_paragraph_with_style(self):
        proj = self._make_doc()
        item = add_paragraph(
            proj, text="Styled", style={"bold": True, "font_size": "14pt"}
        )
        assert item["style"]["bold"] is True
        assert item["style"]["font_size"] == "14pt"

    def test_add_heading(self):
        proj = self._make_doc()
        item = add_heading(proj, text="Title", level=1)
        assert item["type"] == "heading"
        assert item["level"] == 1

    def test_add_heading_level_range(self):
        proj = self._make_doc()
        add_heading(proj, text="H1", level=1)
        add_heading(proj, text="H6", level=6)
        assert len(proj["content"]) == 2

    def test_add_heading_invalid_level(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Heading level"):
            add_heading(proj, level=7)

    def test_add_list_bullet(self):
        proj = self._make_doc()
        item = add_list(proj, items=["A", "B", "C"], list_style="bullet")
        assert item["type"] == "list"
        assert item["list_style"] == "bullet"
        assert len(item["items"]) == 3

    def test_add_list_number(self):
        proj = self._make_doc()
        item = add_list(proj, items=["First", "Second"], list_style="number")
        assert item["list_style"] == "number"

    def test_add_list_invalid_style(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="Invalid list style"):
            add_list(proj, list_style="roman")

    def test_add_table(self):
        proj = self._make_doc()
        item = add_table(proj, rows=3, cols=4)
        assert item["type"] == "table"
        assert item["rows"] == 3
        assert item["cols"] == 4
        assert len(item["data"]) == 3
        assert len(item["data"][0]) == 4

    def test_add_table_with_data(self):
        proj = self._make_doc()
        data = [["Name", "Age"], ["Alice", "30"]]
        item = add_table(proj, rows=2, cols=2, data=data)
        assert item["data"][0][0] == "Name"

    def test_add_table_invalid_dims(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="at least 1"):
            add_table(proj, rows=0, cols=2)

    def test_add_page_break(self):
        proj = self._make_doc()
        item = add_page_break(proj)
        assert item["type"] == "page_break"

    def test_add_at_position(self):
        proj = self._make_doc()
        add_paragraph(proj, text="First")
        add_paragraph(proj, text="Third")
        add_paragraph(proj, text="Second", position=1)
        assert proj["content"][1]["text"] == "Second"

    def test_add_at_invalid_position(self):
        proj = self._make_doc()
        with pytest.raises(IndexError):
            add_paragraph(proj, text="Bad", position=5)

    def test_remove_content(self):
        proj = self._make_doc()
        add_paragraph(proj, text="A")
        add_paragraph(proj, text="B")
        removed = remove_content(proj, 0)
        assert removed["text"] == "A"
        assert len(proj["content"]) == 1

    def test_remove_content_empty(self):
        proj = self._make_doc()
        with pytest.raises(ValueError, match="No content"):
            remove_content(proj, 0)

    def test_list_content(self):
        proj = self._make_doc()
        add_heading(proj, text="Title", level=1)
        add_paragraph(proj, text="Body text")
        add_list(proj, items=["A", "B"])
        result = list_content(proj)
        assert len(result) == 3
        assert result[0]["type"] == "heading"
        assert result[1]["type"] == "paragraph"
        assert result[2]["type"] == "list"

    def test_get_content(self):
        proj = self._make_doc()
        add_paragraph(proj, text="Test")
        item = get_content(proj, 0)
        assert item["text"] == "Test"

    def test_set_content_text(self):
        proj = self._make_doc()
        add_paragraph(proj, text="Old")
        item = set_content_text(proj, 0, "New")
        assert item["text"] == "New"

    def test_set_content_text_on_table(self):
        proj = self._make_doc()
        add_table(proj)
        with pytest.raises(ValueError, match="Cannot set text"):
            set_content_text(proj, 0, "Text")

    def test_writer_rejects_calc(self):
        proj = create_document(doc_type="calc")
        with pytest.raises(ValueError, match="expected 'writer'"):
            add_paragraph(proj, text="Hello")
