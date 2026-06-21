# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestStyleParsing:
    def test_parse_empty(self):
        assert drawio_xml.parse_style("") == {}

    def test_parse_basic(self):
        style = drawio_xml.parse_style("rounded=1;whiteSpace=wrap;html=1;")
        assert style["rounded"] == "1"
        assert style["whiteSpace"] == "wrap"
        assert style["html"] == "1"

    def test_parse_base_style(self):
        style = drawio_xml.parse_style("ellipse;whiteSpace=wrap;html=1;")
        assert style["ellipse"] == ""
        assert style["html"] == "1"

    def test_build_style(self):
        style = drawio_xml.build_style({"rounded": "1", "html": "1"})
        assert "rounded=1" in style
        assert "html=1" in style

    def test_roundtrip(self):
        original = "rounded=1;whiteSpace=wrap;html=1;"
        style = drawio_xml.parse_style(original)
        rebuilt = drawio_xml.build_style(style)
        reparsed = drawio_xml.parse_style(rebuilt)
        assert style == reparsed

    def test_set_style_property(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50)
        cell = drawio_xml.find_cell_by_id(root, v1)
        drawio_xml.set_style_property(cell, "fillColor", "#ff0000")
        style = drawio_xml.parse_style(cell.get("style", ""))
        assert style["fillColor"] == "#ff0000"

    def test_remove_style_property(self):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50)
        cell = drawio_xml.find_cell_by_id(root, v1)
        drawio_xml.set_style_property(cell, "fillColor", "#ff0000")
        drawio_xml.remove_style_property(cell, "fillColor")
        style = drawio_xml.parse_style(cell.get("style", ""))
        assert "fillColor" not in style


class TestShapePresets:
    @pytest.mark.parametrize("shape_type", list(drawio_xml.SHAPE_STYLES.keys()))
    def test_all_shape_types(self, shape_type):
        root = drawio_xml.create_blank_diagram()
        cell_id = drawio_xml.add_vertex(root, shape_type, 0, 0, 100, 60, shape_type)
        assert cell_id is not None
        cell = drawio_xml.find_cell_by_id(root, cell_id)
        assert cell is not None
        assert cell.get("value") == shape_type

    @pytest.mark.parametrize("edge_style", list(drawio_xml.EDGE_STYLES.keys()))
    def test_all_edge_styles(self, edge_style):
        root = drawio_xml.create_blank_diagram()
        v1 = drawio_xml.add_vertex(root, "rectangle", 0, 0, 100, 50, "A")
        v2 = drawio_xml.add_vertex(root, "rectangle", 200, 0, 100, 50, "B")
        edge_id = drawio_xml.add_edge(root, v1, v2, edge_style)
        assert edge_id is not None
        edge = drawio_xml.find_cell_by_id(root, edge_id)
        assert edge is not None
        assert edge.get("edge") == "1"


class TestPages:
    def test_single_page_default(self):
        root = drawio_xml.create_blank_diagram()
        pages = drawio_xml.list_pages(root)
        assert len(pages) == 1
        assert pages[0]["name"] == "Page-1"

    def test_add_page(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.add_page(root, "Second Page")
        pages = drawio_xml.list_pages(root)
        assert len(pages) == 2
        assert pages[1]["name"] == "Second Page"

    def test_remove_page(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.add_page(root, "To Remove")
        assert len(drawio_xml.list_pages(root)) == 2
        drawio_xml.remove_page(root, 1)
        assert len(drawio_xml.list_pages(root)) == 1

    def test_cannot_remove_last_page(self):
        root = drawio_xml.create_blank_diagram()
        with pytest.raises(RuntimeError, match="Cannot remove the last page"):
            drawio_xml.remove_page(root, 0)

    def test_rename_page(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.rename_page(root, 0, "My Diagram")
        pages = drawio_xml.list_pages(root)
        assert pages[0]["name"] == "My Diagram"

    def test_shapes_on_different_pages(self):
        root = drawio_xml.create_blank_diagram()
        drawio_xml.add_vertex(
            root, "rectangle", 0, 0, 100, 50, "Page1Shape", diagram_index=0
        )
        drawio_xml.add_page(root, "Page 2")
        drawio_xml.add_vertex(
            root, "ellipse", 0, 0, 80, 80, "Page2Shape", diagram_index=1
        )
        assert len(drawio_xml.get_vertices(root, 0)) == 1
        assert len(drawio_xml.get_vertices(root, 1)) == 1
