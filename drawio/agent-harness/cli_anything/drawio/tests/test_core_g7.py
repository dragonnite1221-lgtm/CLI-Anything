# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestWorkflows:
    def test_flowchart(self):
        """Build a complete flowchart: Start → Process → Decision → End."""
        s = Session()
        proj_mod.new_project(s, "letter")

        start = shapes_mod.add_shape(s, "ellipse", 350, 50, 120, 60, "Start")["id"]
        process = shapes_mod.add_shape(
            s, "rectangle", 340, 170, 140, 60, "Process Data"
        )["id"]
        decision = shapes_mod.add_shape(s, "diamond", 340, 290, 140, 80, "Valid?")["id"]
        end = shapes_mod.add_shape(s, "ellipse", 350, 430, 120, 60, "End")["id"]

        conn_mod.add_connector(s, start, process)
        conn_mod.add_connector(s, process, decision)
        conn_mod.add_connector(s, decision, end, label="Yes")

        shapes = shapes_mod.list_shapes(s)
        assert len(shapes) == 4
        connectors = conn_mod.list_connectors(s)
        assert len(connectors) == 3

        # Save and reopen
        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            s2 = Session()
            proj_mod.open_project(s2, path)
            assert len(drawio_xml.get_vertices(s2.root)) == 4
            assert len(drawio_xml.get_edges(s2.root)) == 3
        finally:
            os.unlink(path)

    def test_styled_diagram(self):
        """Build a diagram with custom styles."""
        s = Session()
        proj_mod.new_project(s)

        box = shapes_mod.add_shape(s, "rounded", 100, 100, 160, 80, "Styled Box")["id"]
        shapes_mod.set_style(s, box, "fillColor", "#dae8fc")
        shapes_mod.set_style(s, box, "strokeColor", "#6c8ebf")
        shapes_mod.set_style(s, box, "fontSize", "16")
        shapes_mod.set_style(s, box, "shadow", "1")

        info = shapes_mod.get_shape_info(s, box)
        assert info["style_parsed"]["fillColor"] == "#dae8fc"
        assert info["style_parsed"]["strokeColor"] == "#6c8ebf"
        assert info["style_parsed"]["fontSize"] == "16"
        assert info["style_parsed"]["shadow"] == "1"

    def test_multi_page_workflow(self):
        """Create a multi-page document."""
        s = Session()
        proj_mod.new_project(s)

        # Page 1: Architecture diagram
        pages_mod.rename_page(s, 0, "Architecture")
        shapes_mod.add_shape(s, "cylinder", 100, 100, 80, 100, "Database")
        shapes_mod.add_shape(s, "rectangle", 300, 100, 120, 60, "API Server")

        # Page 2: Flowchart
        pages_mod.add_page(s, "Flowchart")
        shapes_mod.add_shape(s, "ellipse", 100, 100, 100, 50, "Start", diagram_index=1)

        result = pages_mod.list_pages(s)
        assert len(result) == 2
        assert result[0]["name"] == "Architecture"
        assert result[1]["name"] == "Flowchart"

    def test_undo_redo_workflow(self):
        """Test undo/redo across multiple operations."""
        s = Session()
        proj_mod.new_project(s)

        shapes_mod.add_shape(s, "rectangle", label="First")
        shapes_mod.add_shape(s, "rectangle", 200, 100, label="Second")
        shapes_mod.add_shape(s, "rectangle", 400, 100, label="Third")

        assert len(shapes_mod.list_shapes(s)) == 3
        s.undo()
        assert len(shapes_mod.list_shapes(s)) == 2
        s.undo()
        assert len(shapes_mod.list_shapes(s)) == 1
        s.redo()
        assert len(shapes_mod.list_shapes(s)) == 2
        s.redo()
        assert len(shapes_mod.list_shapes(s)) == 3

    def test_export_xml_workflow(self):
        """Full workflow: create diagram, add content, export to XML."""
        s = Session()
        proj_mod.new_project(s)

        v1 = shapes_mod.add_shape(s, "rectangle", 100, 100, 120, 60, "Server")["id"]
        v2 = shapes_mod.add_shape(s, "cylinder", 300, 100, 80, 100, "DB")["id"]
        conn_mod.add_connector(s, v1, v2, "orthogonal", "query")

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name

        try:
            result = export_mod.render(s, path, fmt="xml", overwrite=True)
            assert result["file_size"] > 0

            # Verify exported content
            parsed = drawio_xml.parse_drawio(path)
            vertices = drawio_xml.get_vertices(parsed)
            edges = drawio_xml.get_edges(parsed)
            assert len(vertices) == 2
            assert len(edges) == 1
        finally:
            os.unlink(path)
