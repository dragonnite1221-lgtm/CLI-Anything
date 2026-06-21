# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExport:
    def test_list_formats(self):
        formats = export_mod.list_formats()
        names = [f["name"] for f in formats]
        assert "png" in names
        assert "pdf" in names
        assert "svg" in names

    def test_export_xml_direct(self):
        """XML export doesn't need draw.io CLI."""
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", label="ExportTest")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name

        try:
            result = export_mod.render(s, path, fmt="xml", overwrite=True)
            assert result["action"] == "export"
            assert result["format"] == "xml"
            assert result["method"] == "direct-write"
            assert os.path.exists(path)
            assert result["file_size"] > 0

            # Verify the XML is valid drawio
            parsed = drawio_xml.parse_drawio(path)
            assert parsed.tag == "mxfile"
            cells = drawio_xml.get_all_cells(parsed)
            assert len(cells) == 1
        finally:
            os.unlink(path)

    def test_export_no_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project is open"):
            export_mod.render(s, "test.png")

    def test_export_invalid_format(self):
        s = Session()
        proj_mod.new_project(s)
        with pytest.raises(ValueError, match="Unknown format"):
            export_mod.render(s, "test.bmp", fmt="bmp")

    def test_export_file_exists(self):
        s = Session()
        proj_mod.new_project(s)
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name

        try:
            with pytest.raises(FileExistsError):
                export_mod.render(s, path, fmt="xml", overwrite=False)
        finally:
            os.unlink(path)
