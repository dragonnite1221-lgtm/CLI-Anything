# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDrawioXml:
    def test_create_blank_diagram(self):
        root = drawio_xml.create_blank_diagram(850, 1100)
        assert root.tag == "mxfile"
        diagrams = root.findall("diagram")
        assert len(diagrams) == 1
        model = diagrams[0].find("mxGraphModel")
        assert model is not None
        assert model.get("pageWidth") == "850"
        assert model.get("pageHeight") == "1100"

    def test_system_cells_present(self):
        root = drawio_xml.create_blank_diagram()
        xml_root = drawio_xml.get_root(root)
        cells = xml_root.findall("mxCell")
        ids = [c.get("id") for c in cells]
        assert "0" in ids
        assert "1" in ids

    def test_no_user_cells_in_blank(self):
        root = drawio_xml.create_blank_diagram()
        assert len(drawio_xml.get_all_cells(root)) == 0

    def test_add_vertex(self):
        root = drawio_xml.create_blank_diagram()
        cell_id = drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "Test")
        assert cell_id is not None
        cells = drawio_xml.get_all_cells(root)
        assert len(cells) == 1
        assert cells[0].get("value") == "Test"
        assert cells[0].get("vertex") == "1"

    def test_add_edge(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "A")
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 20, 120, 60, "B")
        e1 = drawio_xml.add_edge(root, v1, v2, "orthogonal", "connects")
        assert e1 is not None
        edges = drawio_xml.get_edges(root)
        assert len(edges) == 1
        assert edges[0].get("source") == v1
        assert edges[0].get("target") == v2
        assert edges[0].get("value") == "connects"

    def test_add_vertex_custom_id(self):
        root = drawio_xml.create_blank_diagram()
        cell_id = drawio_xml.add_vertex(
            root, "rectangle", 0, 0, 100, 50, "X", cell_id="my-node"
        )
        assert cell_id == "my-node"
        assert drawio_xml.find_cell_by_id(root, "my-node") is not None

    def test_add_vertex_duplicate_id_raises(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50, cell_id="dup")
        with pytest.raises(ValueError, match="already exists"):
            drawio_xml.add_vertex(root, "ellipse", 200, 0, 100, 50, cell_id="dup")

    def test_add_edge_custom_id(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50)
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 0, 100, 50)
        edge_id = drawio_xml.add_edge(root, v1, v2, edge_id="my-edge")
        assert edge_id == "my-edge"
        assert drawio_xml.find_cell_by_id(root, "my-edge") is not None

    def test_add_edge_duplicate_id_raises(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50)
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 0, 100, 50)
        drawio_xml.add_edge(root, v1, v2, edge_id="dup-edge")
        with pytest.raises(ValueError, match="already exists"):
            drawio_xml.add_edge(root, v1, v2, edge_id="dup-edge")

    def test_remove_cell(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "A")
        assert len(drawio_xml.get_all_cells(root)) == 1
        drawio_xml.remove_cell(root, v1)
        assert len(drawio_xml.get_all_cells(root)) == 0

    def test_remove_vertex_also_removes_edges(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "A")
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 20, 120, 60, "B")
        drawio_xml.add_edge(root, v1, v2)
        assert len(drawio_xml.get_edges(root)) == 1
        drawio_xml.remove_cell(root, v1)
        assert len(drawio_xml.get_edges(root)) == 0

    def test_find_cell_by_id(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "ellipse", 10, 20, 100, 100, "Circle")
        found = drawio_xml.find_cell_by_id(root, v1)
        assert found is not None
        assert found.get("value") == "Circle"

    def test_find_cell_not_exists(self):
        root = drawio_xml.create_blank_diagram()
        assert drawio_xml.find_cell_by_id(root, "nonexistent") is None

    def test_update_cell_label(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50, "Old")
        drawio_xml.update_cell_label(root, v1, "New")
        cell = drawio_xml.find_cell_by_id(root, v1)
        assert cell.get("value") == "New"

    def test_move_cell(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 100, 50)
        drawio_xml.move_cell(root, v1, 300, 400)
        geo = drawio_xml.get_cell_geometry(drawio_xml.find_cell_by_id(root, v1))
        assert geo["x"] == 300.0
        assert geo["y"] == 400.0

    def test_resize_cell(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 100, 50)
        drawio_xml.resize_cell(root, v1, 200, 150)
        geo = drawio_xml.get_cell_geometry(drawio_xml.find_cell_by_id(root, v1))
        assert geo["width"] == 200.0
        assert geo["height"] == 150.0

    def test_get_cell_info(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "Hello")
        info = drawio_xml.get_cell_info(drawio_xml.find_cell_by_id(root, v1))
        assert info["id"] == v1
        assert info["value"] == "Hello"
        assert info["type"] == "vertex"
        assert info["width"] == 120.0

    def test_get_vertices(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50)
        drawio_xml.add_vertex(root, "ellipse", 200, 0, 100, 100)
        v1 = drawio_xml.add_vertex(root, "diamond", 0, 200, 80, 80)
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 200, 100, 50)
        drawio_xml.add_edge(root, v1, v2)
        assert len(drawio_xml.get_vertices(root)) == 4
        assert len(drawio_xml.get_edges(root)) == 1

    def test_write_and_parse_roundtrip(self):
        root = drawio_xml.create_blank_diagram(1200, 800)
        drawio_xml.add_vertex(root, "rectangle", 10, 20, 120, 60, "Test Shape")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name

        try:
            drawio_xml.write_drawio(root, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

            parsed = drawio_xml.parse_drawio(path)
            assert parsed.tag == "mxfile"
            cells = drawio_xml.get_all_cells(parsed)
            assert len(cells) == 1
            assert cells[0].get("value") == "Test Shape"
        finally:
            os.unlink(path)
