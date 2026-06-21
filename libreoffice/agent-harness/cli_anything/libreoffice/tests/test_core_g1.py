# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestImport:
    def test_list_import_formats_includes_office_and_odf(self):
        formats = importer_mod.list_import_formats()
        extensions = {item["extension"] for item in formats}
        assert ".odt" in extensions
        assert ".docx" in extensions
        assert ".xlsx" in extensions
        assert ".pptx" in extensions

    def test_import_writer_odt(self):
        proj = create_document(doc_type="writer", name="import_writer")
        add_heading(proj, text="Imported Heading", level=2)
        add_paragraph(proj, text="Imported paragraph")
        add_list(proj, items=["One", "Two"])
        add_table(proj, rows=2, cols=2, data=[["A", "B"], ["C", "D"]])

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "writer.odt")
            to_odt(proj, path)
            imported = importer_mod.import_document(path)

        assert imported["type"] == "writer"
        assert imported["metadata"]["import_method"] == "native-odf"
        assert [item["type"] for item in imported["content"]] == [
            "heading",
            "paragraph",
            "list",
            "table",
        ]
        assert imported["content"][0]["text"] == "Imported Heading"
        assert imported["content"][0]["level"] == 2
        assert imported["content"][3]["data"][1][1] == "D"

    def test_import_calc_ods(self):
        proj = create_document(doc_type="calc", name="import_calc")
        set_cell(proj, "A1", "Name")
        set_cell(proj, "B1", "42", cell_type="float")

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sheet.ods")
            to_ods(proj, path)
            imported = importer_mod.import_document(path)

        assert imported["type"] == "calc"
        assert imported["sheets"][0]["name"] == "Sheet1"
        assert imported["sheets"][0]["cells"]["A1"]["value"] == "Name"
        assert imported["sheets"][0]["cells"]["B1"]["value"] == 42.0
        assert imported["sheets"][0]["cells"]["B1"]["type"] == "float"

    def test_import_calc_formula_normalizes_odf_prefix(self):
        proj = create_document(doc_type="calc", name="formula_calc")
        set_cell(proj, "A1", "1", cell_type="float")
        set_cell(proj, "A2", "2", cell_type="float")
        set_cell(proj, "A3", "0", cell_type="float", formula="=A1+A2")

        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "formula.ods")
            roundtrip = os.path.join(tmp, "roundtrip.ods")
            to_ods(proj, source)
            imported = importer_mod.import_document(source)
            to_ods(imported, roundtrip)
            content_xml = parse_odf(roundtrip)["content_xml"]

        formula = imported["sheets"][0]["cells"]["A3"]["formula"]
        assert formula == "=A1+A2"
        assert 'table:formula="of:=A1+A2"' in content_xml
        assert "of:of:=" not in content_xml

    def test_import_impress_odp(self):
        proj = create_document(doc_type="impress", name="import_impress")
        add_slide(proj, title="Intro", content="Welcome")
        add_slide(proj, title="End", content="Questions")

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deck.odp")
            to_odp(proj, path)
            imported = importer_mod.import_document(path)

        assert imported["type"] == "impress"
        assert len(imported["slides"]) == 2
        assert imported["slides"][0]["title"] == "Intro"
        assert imported["slides"][0]["content"] == "Welcome"

    def test_import_docx_uses_libreoffice_conversion(self, monkeypatch):
        source_proj = create_document(doc_type="writer")
        add_paragraph(source_proj, text="Converted content")

        with tempfile.TemporaryDirectory() as tmp:
            odt_path = os.path.join(tmp, "converted.odt")
            to_odt(source_proj, odt_path)
            docx_path = os.path.join(tmp, "input.docx")
            with open(docx_path, "wb") as f:
                f.write(b"fake docx; conversion is monkeypatched")

            def fake_convert(input_path, output_format, output_dir=None, timeout=120):
                assert input_path == docx_path
                assert output_format == "odt"
                out = os.path.join(output_dir, "input.odt")
                shutil.copyfile(odt_path, out)
                return out

            monkeypatch.setattr(importer_mod, "convert", fake_convert)
            imported = importer_mod.import_document(docx_path)

        assert imported["type"] == "writer"
        assert imported["metadata"]["import_method"] == "libreoffice-headless"
        assert imported["metadata"]["original_format"] == "docx"
        assert imported["content"][0]["text"] == "Converted content"

    def test_reject_unsupported_import_format(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError, match="Unsupported import format"):
                importer_mod.import_document(path)
        finally:
            os.unlink(path)

    def test_reject_invalid_odf_file(self):
        with tempfile.NamedTemporaryFile(suffix=".odt", delete=False) as f:
            f.write(b"not a zip")
            path = f.name
        try:
            with pytest.raises(ValueError, match="Invalid ODF file"):
                importer_mod.import_document(path)
        finally:
            os.unlink(path)

    def test_reject_malformed_odf_meta_xml(self):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="body")

        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "source.odt")
            malformed = os.path.join(tmp, "malformed.odt")
            to_odt(proj, source)

            with (
                zipfile.ZipFile(source, "r") as zin,
                zipfile.ZipFile(malformed, "w") as zout,
            ):
                for info in zin.infolist():
                    data = zin.read(info.filename)
                    if info.filename == "meta.xml":
                        data = b"<broken>"
                    zout.writestr(info, data)

            with pytest.raises(ValueError, match="Invalid ODF meta.xml"):
                importer_mod.import_document(malformed)
