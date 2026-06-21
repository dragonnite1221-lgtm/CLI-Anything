# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestFileRoundtrip:
    """Create real .drawio files, save, reopen, verify content."""

    def test_empty_diagram_roundtrip(self):
        s = Session()
        proj_mod.new_project(s, "letter")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            assert os.path.exists(path)
            size = os.path.getsize(path)
            assert size > 0
            print(f"\n  Empty diagram: {path} ({size:,} bytes)")

            # Reopen and verify structure
            s2 = Session()
            proj_mod.open_project(s2, path)
            assert s2.is_open
            info = proj_mod.project_info(s2)
            assert len(info["shapes"]) == 0
            assert len(info["edges"]) == 0
        finally:
            os.unlink(path)

    def test_complex_diagram_roundtrip(self):
        """Build a complex diagram, save, reopen, verify all content."""
        s = Session()
        proj_mod.new_project(s, "16:9")

        # Add diverse shapes
        shapes = {}
        for i, (shape_type, label) in enumerate(
            [
                ("rectangle", "Server"),
                ("cylinder", "Database"),
                ("ellipse", "Client"),
                ("cloud", "Internet"),
                ("hexagon", "Load Balancer"),
                ("diamond", "Decision"),
            ]
        ):
            r = shapes_mod.add_shape(
                s,
                shape_type,
                x=100 + (i % 3) * 200,
                y=100 + (i // 3) * 200,
                width=120,
                height=60,
                label=label,
            )
            shapes[label] = r["id"]

        # Add connectors
        conn_mod.add_connector(s, shapes["Client"], shapes["Internet"], label="request")
        conn_mod.add_connector(s, shapes["Internet"], shapes["Load Balancer"])
        conn_mod.add_connector(s, shapes["Load Balancer"], shapes["Server"])
        conn_mod.add_connector(s, shapes["Server"], shapes["Database"], label="query")

        # Apply styles
        shapes_mod.set_style(s, shapes["Server"], "fillColor", "#dae8fc")
        shapes_mod.set_style(s, shapes["Database"], "fillColor", "#d5e8d4")
        shapes_mod.set_style(s, shapes["Client"], "fillColor", "#fff2cc")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            file_size = os.path.getsize(path)
            print(f"\n  Complex diagram: {path} ({file_size:,} bytes)")
            print(f"  Shapes: {len(shapes)}, Connectors: 4")

            # Reopen and verify
            s2 = Session()
            result = proj_mod.open_project(s2, path)
            assert result["shape_count"] == 6
            assert result["edge_count"] == 4

            # Verify shape labels preserved
            for cell in drawio_xml.get_vertices(s2.root):
                assert cell.get("value") in shapes

            # Verify styles preserved
            server_cell = drawio_xml.find_cell_by_id(s2.root, shapes["Server"])
            style = drawio_xml.parse_style(server_cell.get("style", ""))
            assert style.get("fillColor") == "#dae8fc"
        finally:
            os.unlink(path)

    def test_multi_page_roundtrip(self):
        """Create multi-page diagram, save, verify all pages."""
        s = Session()
        proj_mod.new_project(s, "letter")
        pages_mod.rename_page(s, 0, "Overview")
        shapes_mod.add_shape(s, "rectangle", label="Main System")

        pages_mod.add_page(s, "Details")
        shapes_mod.add_shape(s, "ellipse", label="Component A", diagram_index=1)
        shapes_mod.add_shape(
            s, "ellipse", 200, 100, label="Component B", diagram_index=1
        )

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)

            s2 = Session()
            proj_mod.open_project(s2, path)
            pages = drawio_xml.list_pages(s2.root)
            assert len(pages) == 2
            assert pages[0]["name"] == "Overview"
            assert pages[1]["name"] == "Details"
            assert pages[0]["cell_count"] == 1
            assert pages[1]["cell_count"] == 2
        finally:
            os.unlink(path)
