# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestOfficeImportE2E:
    """True E2E: existing Office files -> ODF -> project JSON model."""

    def test_import_existing_docx(self, tmp_dir):
        proj = create_document(doc_type="writer", name="Import DOCX")
        add_heading(proj, text="DOCX Source", level=1)
        add_paragraph(proj, text="Paragraph imported from an existing DOCX.")
        docx_path = os.path.join(tmp_dir, "source.docx")
        export(proj, docx_path, preset="docx", overwrite=True)

        imported = importer_mod.import_document(docx_path)

        assert imported["type"] == "writer"
        text = "\n".join(
            [item.get("text", "") for item in imported["content"]]
            + [
                list_item
                for item in imported["content"]
                for list_item in item.get("items", [])
            ]
        )
        assert "DOCX Source" in text
        assert "Paragraph imported from an existing DOCX." in text
        assert imported["metadata"]["import_method"] == "libreoffice-headless"

    def test_import_existing_xlsx(self, tmp_dir):
        proj = create_document(doc_type="calc", name="Import XLSX")
        set_cell(proj, "A1", "Name")
        set_cell(proj, "B1", "Score")
        set_cell(proj, "A2", "Alice")
        set_cell(proj, "B2", "95", cell_type="float")
        xlsx_path = os.path.join(tmp_dir, "source.xlsx")
        export(proj, xlsx_path, preset="xlsx", overwrite=True)

        imported = importer_mod.import_document(xlsx_path)

        assert imported["type"] == "calc"
        cells = imported["sheets"][0]["cells"]
        assert cells["A1"]["value"] == "Name"
        assert cells["A2"]["value"] == "Alice"
        assert cells["B2"]["value"] == 95.0

    def test_import_existing_pptx(self, tmp_dir):
        proj = create_document(doc_type="impress", name="Import PPTX")
        add_slide(proj, title="Opening", content="Imported from PPTX")
        add_slide(proj, title="Closing", content="Done")
        pptx_path = os.path.join(tmp_dir, "source.pptx")
        export(proj, pptx_path, preset="pptx", overwrite=True)

        imported = importer_mod.import_document(pptx_path)

        assert imported["type"] == "impress"
        slide_text = "\n".join(
            f"{slide.get('title', '')}\n{slide.get('content', '')}"
            for slide in imported["slides"]
        )
        assert "Opening" in slide_text
        assert "Imported from PPTX" in slide_text
