# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestODFStructure:
    def test_odt_is_valid_zip(self, tmp_dir):
        proj = create_document(doc_type="writer", name="test")
        add_paragraph(proj, text="Hello world")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)
        assert zipfile.is_zipfile(path)

    def test_odt_mimetype_first_uncompressed(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Test")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            assert names[0] == "mimetype"
            info = zf.getinfo("mimetype")
            assert info.compress_type == zipfile.ZIP_STORED

    def test_odt_mimetype_content(self, tmp_dir):
        proj = create_document(doc_type="writer")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            mimetype = zf.read("mimetype").decode("utf-8")
            assert mimetype == ODF_MIMETYPES["writer"]

    def test_odt_has_required_files(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Content")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "content.xml" in names
            assert "styles.xml" in names
            assert "meta.xml" in names
            assert "META-INF/manifest.xml" in names

    def test_odt_content_xml_valid(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_heading(proj, text="Title", level=1)
        add_paragraph(proj, text="Body text")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            content = zf.read("content.xml").decode("utf-8")
            root = ET.fromstring(content)
            assert root is not None

    def test_odt_styles_xml_valid(self, tmp_dir):
        proj = create_document(doc_type="writer")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            styles = zf.read("styles.xml").decode("utf-8")
            root = ET.fromstring(styles)
            assert root is not None

    def test_odt_meta_xml_valid(self, tmp_dir):
        proj = create_document(doc_type="writer")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        with zipfile.ZipFile(path, "r") as zf:
            meta = zf.read("meta.xml").decode("utf-8")
            root = ET.fromstring(meta)
            assert root is not None

    def test_odt_validate_utility(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_paragraph(proj, text="Validate me")
        path = os.path.join(tmp_dir, "test.odt")
        to_odt(proj, path)

        result = validate_odf(path)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_ods_structure(self, tmp_dir):
        proj = create_document(doc_type="calc")
        set_cell(proj, "A1", "Hello")
        set_cell(proj, "B1", "42", cell_type="float")
        path = os.path.join(tmp_dir, "test.ods")
        to_ods(proj, path)

        result = validate_odf(path)
        assert result["valid"] is True
        with zipfile.ZipFile(path, "r") as zf:
            mimetype = zf.read("mimetype").decode("utf-8")
            assert mimetype == ODF_MIMETYPES["calc"]

    def test_odp_structure(self, tmp_dir):
        proj = create_document(doc_type="impress")
        add_slide(proj, title="Welcome", content="Hello")
        path = os.path.join(tmp_dir, "test.odp")
        to_odp(proj, path)

        result = validate_odf(path)
        assert result["valid"] is True
        with zipfile.ZipFile(path, "r") as zf:
            mimetype = zf.read("mimetype").decode("utf-8")
            assert mimetype == ODF_MIMETYPES["impress"]
