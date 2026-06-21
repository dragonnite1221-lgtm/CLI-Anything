# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestWriterE2E:
    def test_full_document_odt(self, tmp_dir):
        proj = create_document(doc_type="writer", name="Full Report")
        add_heading(proj, text="Introduction", level=1)
        add_paragraph(proj, text="This is the intro paragraph.")
        add_heading(proj, text="Data", level=2)
        add_table(
            proj,
            rows=3,
            cols=3,
            data=[
                ["Name", "Age", "City"],
                ["Alice", "30", "NYC"],
                ["Bob", "25", "LA"],
            ],
        )
        add_list(proj, items=["Point A", "Point B", "Point C"], list_style="bullet")
        add_page_break(proj)
        add_heading(proj, text="Conclusion", level=1)
        add_paragraph(proj, text="In conclusion...")

        path = os.path.join(tmp_dir, "report.odt")
        result = to_odt(proj, path)
        assert os.path.exists(path)
        assert result["format"] == "writer"

        # Validate content
        parsed = parse_odf(path)
        assert "Title" not in parsed.get("mimetype", "")  # just mimetype check
        content_xml = parsed["content_xml"]
        assert "Introduction" in content_xml
        assert "Alice" in content_xml
        assert "Point A" in content_xml

    def test_styled_paragraph_in_odt(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Bold text", style={"bold": True, "font_size": "16pt"})
        path = os.path.join(tmp_dir, "styled.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        content = parsed["content_xml"]
        assert "Bold text" in content
        assert "bold" in content.lower() or "font-weight" in content.lower()

    def test_writer_html_export(self, tmp_dir):
        proj = create_document(doc_type="writer", name="HTML Test")
        add_heading(proj, text="Title", level=1)
        add_paragraph(proj, text="Body text")
        add_list(proj, items=["A", "B"])
        path = os.path.join(tmp_dir, "doc.html")
        result = to_html(proj, path)
        assert os.path.exists(path)

        with open(path) as f:
            html = f.read()
        assert "<h1>Title</h1>" in html
        assert "<p>Body text</p>" in html
        assert "<li>A</li>" in html

    def test_writer_text_export(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_heading(proj, text="Header", level=1)
        add_paragraph(proj, text="Paragraph text")
        add_list(proj, items=["X", "Y"], list_style="number")
        path = os.path.join(tmp_dir, "doc.txt")
        result = to_text(proj, path)
        assert os.path.exists(path)

        with open(path) as f:
            text = f.read()
        assert "# Header" in text
        assert "Paragraph text" in text
        assert "1. X" in text


class TestCalcE2E:
    def test_multi_sheet_ods(self, tmp_dir):
        proj = create_document(doc_type="calc", name="Budget")
        set_cell(proj, "A1", "Item", sheet=0)
        set_cell(proj, "B1", "Cost", sheet=0)
        set_cell(proj, "A2", "Rent", sheet=0)
        set_cell(proj, "B2", "1500", cell_type="float", sheet=0)

        add_sheet(proj, name="Summary")
        set_cell(proj, "A1", "Total", sheet=1)

        path = os.path.join(tmp_dir, "budget.ods")
        to_ods(proj, path)

        result = validate_odf(path)
        assert result["valid"] is True

        parsed = parse_odf(path)
        assert "Item" in parsed["content_xml"]
        assert "Rent" in parsed["content_xml"]
        assert "Summary" in parsed["content_xml"]

    def test_calc_html_export(self, tmp_dir):
        proj = create_document(doc_type="calc")
        set_cell(proj, "A1", "Name")
        set_cell(proj, "B1", "Score")
        set_cell(proj, "A2", "Alice")
        set_cell(proj, "B2", "95")
        path = os.path.join(tmp_dir, "sheet.html")
        to_html(proj, path)

        with open(path) as f:
            html = f.read()
        assert "Name" in html
        assert "Alice" in html
        assert "<table" in html

    def test_calc_text_export(self, tmp_dir):
        proj = create_document(doc_type="calc")
        set_cell(proj, "A1", "X")
        set_cell(proj, "B1", "Y")
        path = os.path.join(tmp_dir, "sheet.txt")
        to_text(proj, path)

        with open(path) as f:
            text = f.read()
        assert "X" in text
        assert "Y" in text
