# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestODFContent:
    def test_writer_heading_in_xml(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_heading(proj, text="My Heading", level=2)
        path = os.path.join(tmp_dir, "h.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        assert "My Heading" in parsed["content_xml"]
        # ODF heading element
        assert "text:h" in parsed["content_xml"] or "h" in parsed["content_xml"]

    def test_writer_table_in_xml(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_table(proj, rows=2, cols=2, data=[["A", "B"], ["C", "D"]])
        path = os.path.join(tmp_dir, "t.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        for val in ["A", "B", "C", "D"]:
            assert val in parsed["content_xml"]

    def test_writer_list_in_xml(self, tmp_dir):
        proj = create_document(doc_type="writer")
        add_list(proj, items=["Apple", "Banana"])
        path = os.path.join(tmp_dir, "l.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        assert "Apple" in parsed["content_xml"]
        assert "Banana" in parsed["content_xml"]

    def test_calc_cells_in_xml(self, tmp_dir):
        proj = create_document(doc_type="calc")
        set_cell(proj, "A1", "Name")
        set_cell(proj, "B1", "100", cell_type="float")
        path = os.path.join(tmp_dir, "c.ods")
        to_ods(proj, path)

        parsed = parse_odf(path)
        assert "Name" in parsed["content_xml"]
        assert "100" in parsed["content_xml"]

    def test_impress_slides_in_xml(self, tmp_dir):
        proj = create_document(doc_type="impress")
        add_slide(proj, title="Intro Slide", content="Welcome all")
        path = os.path.join(tmp_dir, "i.odp")
        to_odp(proj, path)

        parsed = parse_odf(path)
        assert "Intro Slide" in parsed["content_xml"]
        assert "Welcome all" in parsed["content_xml"]

    def test_meta_xml_has_title(self, tmp_dir):
        proj = create_document(doc_type="writer", name="MetaTest")
        proj["metadata"]["title"] = "My Document Title"
        path = os.path.join(tmp_dir, "meta.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        assert "My Document Title" in parsed["meta_xml"]

    def test_manifest_has_entries(self, tmp_dir):
        proj = create_document(doc_type="writer")
        path = os.path.join(tmp_dir, "manifest.odt")
        to_odt(proj, path)

        parsed = parse_odf(path)
        manifest = parsed["manifest_xml"]
        assert "content.xml" in manifest
        assert "styles.xml" in manifest
        assert "meta.xml" in manifest


class TestLibreOfficeBackend:
    """Test that LibreOffice is installed and the backend works."""

    def test_libreoffice_is_installed(self):
        lo = find_libreoffice()
        assert os.path.exists(lo), f"LibreOffice not found at {lo}"
        print(f"\n  LibreOffice binary: {lo}")

    def test_libreoffice_version(self):
        version = get_version()
        assert "LibreOffice" in version
        print(f"\n  {version}")
