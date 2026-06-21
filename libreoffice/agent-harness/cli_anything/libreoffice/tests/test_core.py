# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDocument:
    def test_create_writer(self):
        proj = create_document(doc_type="writer")
        assert proj["type"] == "writer"
        assert proj["version"] == "1.0"
        assert "content" in proj
        assert isinstance(proj["content"], list)

    def test_create_calc(self):
        proj = create_document(doc_type="calc")
        assert proj["type"] == "calc"
        assert "sheets" in proj
        assert len(proj["sheets"]) == 1

    def test_create_impress(self):
        proj = create_document(doc_type="impress")
        assert proj["type"] == "impress"
        assert "slides" in proj

    def test_create_with_name(self):
        proj = create_document(name="My Report")
        assert proj["name"] == "My Report"

    def test_create_with_profile(self):
        proj = create_document(profile="a4_portrait")
        assert proj["settings"]["page_width"] == "21cm"
        assert proj["settings"]["page_height"] == "29.7cm"

    def test_create_with_letter_profile(self):
        proj = create_document(profile="letter_portrait")
        assert proj["settings"]["page_width"] == "21.59cm"

    def test_create_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid document type"):
            create_document(doc_type="spreadsheet")

    def test_create_invalid_profile(self):
        with pytest.raises(ValueError, match="Unknown profile"):
            create_document(profile="bogus")

    def test_save_and_open(self):
        proj = create_document(name="roundtrip_test")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_document(proj, path)
            loaded = open_document(path)
            assert loaded["name"] == "roundtrip_test"
            assert loaded["type"] == "writer"
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_document("/nonexistent/file.json")

    def test_open_invalid_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"foo": "bar"}, f)
            path = f.name
        try:
            with pytest.raises(ValueError, match="Invalid project file"):
                open_document(path)
        finally:
            os.unlink(path)

    def test_open_odt_as_project_gives_import_hint(self):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Existing file")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "existing.odt")
            to_odt(proj, path)
            with pytest.raises(ValueError, match="document import"):
                open_document(path)

    def test_get_document_info_writer(self):
        proj = create_document(name="info_test", doc_type="writer")
        info = get_document_info(proj)
        assert info["name"] == "info_test"
        assert info["type"] == "writer"
        assert info["content_count"] == 0

    def test_get_document_info_calc(self):
        proj = create_document(doc_type="calc")
        info = get_document_info(proj)
        assert info["sheet_count"] == 1

    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) > 0
        names = [p["name"] for p in profiles]
        assert "a4_portrait" in names
        assert "letter_portrait" in names

    def test_metadata_populated(self):
        proj = create_document()
        assert "metadata" in proj
        assert "created" in proj["metadata"]
        assert proj["metadata"]["software"] == "libreoffice-cli 1.0"
