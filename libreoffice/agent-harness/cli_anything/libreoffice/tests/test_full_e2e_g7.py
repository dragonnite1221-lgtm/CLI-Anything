# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCalcToXLSX:
    """True E2E: Calc spreadsheet -> ODS -> XLSX via LibreOffice headless."""

    def test_calc_to_xlsx(self, tmp_dir):
        proj = create_document(doc_type="calc", name="Spreadsheet Test")
        set_cell(proj, "A1", "Item")
        set_cell(proj, "B1", "Cost")
        set_cell(proj, "A2", "Rent")
        set_cell(proj, "B2", "1500", cell_type="float")
        set_cell(proj, "A3", "Food")
        set_cell(proj, "B3", "600", cell_type="float")

        xlsx_path = os.path.join(tmp_dir, "budget.xlsx")
        result = export(proj, xlsx_path, preset="xlsx", overwrite=True)

        assert os.path.exists(result["output"])
        assert result["format"] == "xlsx"
        assert zipfile.is_zipfile(result["output"]), (
            "XLSX is not a valid ZIP/OOXML file"
        )
        with zipfile.ZipFile(result["output"]) as zf:
            names = zf.namelist()
            assert "[Content_Types].xml" in names
            # XLSX should contain a sheet
            assert any("sheet" in n.lower() for n in names), (
                f"No sheet found in XLSX. Files: {names}"
            )
        print(f"\n  XLSX output: {result['output']} ({result['file_size']:,} bytes)")

    def test_calc_to_csv(self, tmp_dir):
        proj = create_document(doc_type="calc", name="CSV Test")
        set_cell(proj, "A1", "Name")
        set_cell(proj, "B1", "Score")
        set_cell(proj, "A2", "Alice")
        set_cell(proj, "B2", "95", cell_type="float")

        csv_path = os.path.join(tmp_dir, "scores.csv")
        result = export(proj, csv_path, preset="csv", overwrite=True)

        assert os.path.exists(result["output"])
        with open(result["output"]) as f:
            content = f.read()
        # CSV should contain our data
        assert "Name" in content or "Alice" in content, (
            f"CSV doesn't contain expected data: {content[:200]}"
        )
        print(f"\n  CSV output: {result['output']} ({result['file_size']:,} bytes)")
        print(f"  CSV content:\n{content}")

    def test_calc_to_pdf(self, tmp_dir):
        proj = create_document(doc_type="calc", name="PDF Calc")
        set_cell(proj, "A1", "Budget Item")
        set_cell(proj, "B1", "Amount")
        set_cell(proj, "A2", "Salary")
        set_cell(proj, "B2", "5000", cell_type="float")

        pdf_path = os.path.join(tmp_dir, "calc.pdf")
        result = export(proj, pdf_path, preset="pdf", overwrite=True)

        assert os.path.exists(result["output"])
        with open(result["output"], "rb") as f:
            assert f.read(5) == b"%PDF-"
        print(f"\n  Calc PDF: {result['output']} ({result['file_size']:,} bytes)")


class TestImpressToPPTX:
    """True E2E: Impress presentation -> ODP -> PPTX via LibreOffice headless."""

    def test_impress_to_pptx(self, tmp_dir):
        proj = create_document(doc_type="impress", name="Presentation Test")
        add_slide(proj, title="Welcome", content="Our Annual Report")
        add_slide(proj, title="Key Metrics", content="Revenue: $10M\nGrowth: 25%")
        add_slide(proj, title="Thank You", content="Questions?")

        pptx_path = os.path.join(tmp_dir, "deck.pptx")
        result = export(proj, pptx_path, preset="pptx", overwrite=True)

        assert os.path.exists(result["output"])
        assert result["format"] == "pptx"
        assert zipfile.is_zipfile(result["output"]), (
            "PPTX is not a valid ZIP/OOXML file"
        )
        with zipfile.ZipFile(result["output"]) as zf:
            names = zf.namelist()
            assert "[Content_Types].xml" in names
            assert any("slide" in n.lower() for n in names), (
                f"No slides found in PPTX. Files: {names}"
            )
        print(f"\n  PPTX output: {result['output']} ({result['file_size']:,} bytes)")

    def test_impress_to_pdf(self, tmp_dir):
        proj = create_document(doc_type="impress", name="PDF Deck")
        add_slide(proj, title="Title Slide", content="Subtitle text")
        add_slide(proj, title="Content Slide", content="Bullet points here")

        pdf_path = os.path.join(tmp_dir, "slides.pdf")
        result = export(proj, pdf_path, preset="pdf", overwrite=True)

        assert os.path.exists(result["output"])
        with open(result["output"], "rb") as f:
            assert f.read(5) == b"%PDF-"
        print(f"\n  Impress PDF: {result['output']} ({result['file_size']:,} bytes)")
