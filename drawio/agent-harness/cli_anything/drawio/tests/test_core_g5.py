# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestConnectors:
    def test_add_connector(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        result = conn_mod.add_connector(s, v1, v2, "orthogonal", "flow")
        assert result["action"] == "add_connector"
        assert result["source"] == v1
        assert result["target"] == v2
        assert result["label"] == "flow"

    def test_add_connector_invalid_source(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        with pytest.raises(ValueError, match="Source cell not found"):
            conn_mod.add_connector(s, "nonexistent", v1)

    def test_add_connector_invalid_target(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        with pytest.raises(ValueError, match="Target cell not found"):
            conn_mod.add_connector(s, v1, "nonexistent")

    def test_list_connectors(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        conn_mod.add_connector(s, v1, v2)
        result = conn_mod.list_connectors(s)
        assert len(result) == 1

    def test_remove_connector(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        edge = conn_mod.add_connector(s, v1, v2)
        conn_mod.remove_connector(s, edge["id"])
        assert len(conn_mod.list_connectors(s)) == 0

    def test_update_connector_label(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        edge = conn_mod.add_connector(s, v1, v2, label="old")
        conn_mod.update_connector_label(s, edge["id"], "new")
        connectors = conn_mod.list_connectors(s)
        assert connectors[0]["value"] == "new"

    def test_set_connector_style(self):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        edge = conn_mod.add_connector(s, v1, v2)
        conn_mod.set_connector_style(s, edge["id"], "strokeColor", "#0000ff")
        cell = drawio_xml.find_cell_by_id(s.root, edge["id"])
        style = drawio_xml.parse_style(cell.get("style", ""))
        assert style["strokeColor"] == "#0000ff"

    def test_list_edge_styles(self):
        styles = conn_mod.list_edge_styles()
        assert "orthogonal" in styles
        assert "straight" in styles
        assert "curved" in styles

    @pytest.mark.parametrize(
        "edge_style", ["straight", "orthogonal", "curved", "entity-relation"]
    )
    def test_all_edge_styles_via_module(self, edge_style):
        s = Session()
        proj_mod.new_project(s)
        v1 = shapes_mod.add_shape(s, "rectangle", label="A")["id"]
        v2 = shapes_mod.add_shape(s, "rectangle", 200, 100, label="B")["id"]
        result = conn_mod.add_connector(s, v1, v2, edge_style)
        assert result["action"] == "add_connector"


class TestPagesModule:
    def test_list_pages(self):
        s = Session()
        proj_mod.new_project(s)
        result = pages_mod.list_pages(s)
        assert len(result) == 1

    def test_add_page(self):
        s = Session()
        proj_mod.new_project(s)
        result = pages_mod.add_page(s, "Extra Page")
        assert result["action"] == "add_page"
        assert result["page_count"] == 2

    def test_remove_page(self):
        s = Session()
        proj_mod.new_project(s)
        pages_mod.add_page(s, "To Delete")
        pages_mod.remove_page(s, 1)
        assert len(pages_mod.list_pages(s)) == 1

    def test_rename_page(self):
        s = Session()
        proj_mod.new_project(s)
        pages_mod.rename_page(s, 0, "Flowchart")
        result = pages_mod.list_pages(s)
        assert result[0]["name"] == "Flowchart"
