# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestImpressE2E:
    def test_multi_slide_odp(self, tmp_dir):
        proj = create_document(doc_type="impress", name="Deck")
        add_slide(proj, title="Welcome", content="Hello everyone")
        add_slide(proj, title="Agenda", content="1. Intro\n2. Main\n3. Q&A")
        add_slide(proj, title="Thank You")

        path = os.path.join(tmp_dir, "deck.odp")
        to_odp(proj, path)

        result = validate_odf(path)
        assert result["valid"] is True

        parsed = parse_odf(path)
        assert "Welcome" in parsed["content_xml"]
        assert "Agenda" in parsed["content_xml"]

    def test_impress_with_elements(self, tmp_dir):
        proj = create_document(doc_type="impress")
        add_slide(proj, title="Slide 1")
        add_slide_element(proj, 0, text="Custom text box", x="5cm", y="10cm")
        path = os.path.join(tmp_dir, "elem.odp")
        to_odp(proj, path)

        parsed = parse_odf(path)
        assert "Custom text box" in parsed["content_xml"]

    def test_impress_html_export(self, tmp_dir):
        proj = create_document(doc_type="impress")
        add_slide(proj, title="Slide 1", content="Content 1")
        add_slide(proj, title="Slide 2", content="Content 2")
        path = os.path.join(tmp_dir, "pres.html")
        to_html(proj, path)

        with open(path) as f:
            html = f.read()
        assert "Slide 1" in html
        assert "Content 1" in html
        assert "<hr>" in html


class TestExportEdgeCases:
    def test_overwrite_protection(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Test")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path, overwrite=True)
        with pytest.raises(FileExistsError):
            to_odt(proj, path, overwrite=False)

    def test_overwrite_allowed(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="V1")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path, overwrite=True)
        to_odt(proj, path, overwrite=True)
        assert os.path.exists(path)

    def test_export_empty_writer(self, tmp_dir):
        proj = create_document(doc_type="writer")
        path = os.path.join(tmp_dir, "empty.odt")
        to_odt(proj, path)
        result = validate_odf(path)
        assert result["valid"] is True

    def test_export_empty_calc(self, tmp_dir):
        proj = create_document(doc_type="calc")
        path = os.path.join(tmp_dir, "empty.ods")
        to_ods(proj, path)
        result = validate_odf(path)
        assert result["valid"] is True

    def test_export_empty_impress(self, tmp_dir):
        proj = create_document(doc_type="impress")
        path = os.path.join(tmp_dir, "empty.odp")
        to_odp(proj, path)
        result = validate_odf(path)
        assert result["valid"] is True

    def test_export_preset_odt(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Preset test")
        path = os.path.join(tmp_dir, "preset.odt")
        result = export(proj, path, preset="odt")
        assert result["format"] == "writer"
        assert os.path.exists(path)

    def test_export_preset_html(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="HTML preset")
        path = os.path.join(tmp_dir, "preset.html")
        result = export(proj, path, preset="html")
        assert result["format"] == "html"

    def test_export_preset_text(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Text preset")
        path = os.path.join(tmp_dir, "preset.txt")
        result = export(proj, path, preset="text")
        assert result["format"] == "text"

    def test_export_invalid_preset(self, tmp_dir):
        proj = create_document()
        with pytest.raises(ValueError, match="Unknown preset"):
            export(proj, "/tmp/test.xyz", preset="xyz")

    def test_list_presets(self):
        presets = list_presets()
        names = [p["name"] for p in presets]
        assert "odt" in names
        assert "ods" in names
        assert "odp" in names
        assert "html" in names
        assert "text" in names
