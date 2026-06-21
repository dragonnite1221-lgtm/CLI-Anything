# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestXmlExport:
    """Test XML export with content verification."""

    def test_export_xml_valid_structure(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", 100, 100, 120, 60, "ExportTest")
        shapes_mod.add_shape(s, "ellipse", 300, 100, 80, 80, "Circle")
        v1 = shapes_mod.list_shapes(s)[0]["id"]
        v2 = shapes_mod.list_shapes(s)[1]["id"]
        conn_mod.add_connector(s, v1, v2, label="link")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name
        try:
            result = export_mod.render(s, path, fmt="xml", overwrite=True)
            assert result["file_size"] > 0
            print(f"\n  XML export: {path} ({result['file_size']:,} bytes)")

            # Parse and verify XML content
            from xml.etree import ElementTree as ET

            tree = ET.parse(path)
            root = tree.getroot()
            assert root.tag == "mxfile"

            # Count cells
            all_cells = list(root.iter("mxCell"))
            user_cells = [c for c in all_cells if c.get("id") not in ("0", "1")]
            vertices = [c for c in user_cells if c.get("vertex") == "1"]
            edges = [c for c in user_cells if c.get("edge") == "1"]
            assert len(vertices) == 2
            assert len(edges) == 1
            print(f"  Verified: {len(vertices)} vertices, {len(edges)} edges")
        finally:
            os.unlink(path)

    def test_export_xml_preserves_styles(self):
        s = Session()
        proj_mod.new_project(s)
        box = shapes_mod.add_shape(s, "rounded", label="Styled")["id"]
        shapes_mod.set_style(s, box, "fillColor", "#ff6666")
        shapes_mod.set_style(s, box, "strokeWidth", "3")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name
        try:
            export_mod.render(s, path, fmt="xml", overwrite=True)

            parsed = drawio_xml.parse_drawio(path)
            cell = drawio_xml.get_vertices(parsed)[0]
            style = drawio_xml.parse_style(cell.get("style", ""))
            assert style["fillColor"] == "#ff6666"
            assert style["strokeWidth"] == "3"
        finally:
            os.unlink(path)
