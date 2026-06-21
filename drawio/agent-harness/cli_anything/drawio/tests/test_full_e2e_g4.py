# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestRealWorldWorkflows:
    """Simulate actual diagram creation scenarios."""

    def test_architecture_diagram(self):
        """Build a 3-tier web architecture diagram."""
        s = Session()
        proj_mod.new_project(s, "16:9")

        # Tier labels
        client = shapes_mod.add_shape(s, "actor", 100, 50, 60, 80, "User")["id"]
        web = shapes_mod.add_shape(s, "rectangle", 250, 50, 140, 60, "Web Server")["id"]
        app = shapes_mod.add_shape(s, "rectangle", 250, 180, 140, 60, "App Server")[
            "id"
        ]
        db = shapes_mod.add_shape(s, "cylinder", 270, 310, 100, 80, "PostgreSQL")["id"]
        cache = shapes_mod.add_shape(s, "hexagon", 500, 180, 120, 60, "Redis")["id"]

        conn_mod.add_connector(s, client, web, "straight", "HTTPS")
        conn_mod.add_connector(s, web, app, "orthogonal", "REST API")
        conn_mod.add_connector(s, app, db, "orthogonal", "SQL")
        conn_mod.add_connector(s, app, cache, "orthogonal", "cache")

        shapes_mod.set_style(s, web, "fillColor", "#dae8fc")
        shapes_mod.set_style(s, app, "fillColor", "#d5e8d4")
        shapes_mod.set_style(s, db, "fillColor", "#fff2cc")
        shapes_mod.set_style(s, cache, "fillColor", "#f8cecc")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            print(f"\n  Architecture diagram: {path}")
            print(f"  Shapes: 5, Connectors: 4")
            assert os.path.getsize(path) > 0

            # Verify content
            s2 = Session()
            proj_mod.open_project(s2, path)
            assert len(drawio_xml.get_vertices(s2.root)) == 5
            assert len(drawio_xml.get_edges(s2.root)) == 4
        finally:
            os.unlink(path)

    def test_er_diagram(self):
        """Build an entity-relationship diagram."""
        s = Session()
        proj_mod.new_project(s, "letter")

        users = shapes_mod.add_shape(
            s,
            "rectangle",
            100,
            100,
            140,
            100,
            "Users\n─────\nid: int PK\nname: varchar\nemail: varchar",
        )["id"]
        orders = shapes_mod.add_shape(
            s,
            "rectangle",
            400,
            100,
            140,
            100,
            "Orders\n─────\nid: int PK\nuser_id: int FK\ntotal: decimal",
        )["id"]
        products = shapes_mod.add_shape(
            s,
            "rectangle",
            400,
            300,
            140,
            80,
            "Products\n─────\nid: int PK\nname: varchar",
        )["id"]

        conn_mod.add_connector(s, users, orders, "entity-relation", "1:N")
        conn_mod.add_connector(s, orders, products, "entity-relation", "N:M")

        shapes_mod.set_style(s, users, "fillColor", "#e1d5e7")
        shapes_mod.set_style(s, orders, "fillColor", "#e1d5e7")
        shapes_mod.set_style(s, products, "fillColor", "#e1d5e7")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            info = proj_mod.project_info(s)
            assert len(info["shapes"]) == 3
            assert len(info["edges"]) == 2
            print(f"\n  ER diagram: {path}")
        finally:
            os.unlink(path)

    def test_decision_tree(self):
        """Build a decision tree / flowchart."""
        s = Session()
        proj_mod.new_project(s, "letter")

        start = shapes_mod.add_shape(s, "ellipse", 300, 30, 100, 50, "Start")["id"]
        d1 = shapes_mod.add_shape(s, "diamond", 275, 130, 150, 80, "Is it raining?")[
            "id"
        ]
        a1 = shapes_mod.add_shape(s, "rectangle", 100, 280, 140, 50, "Take umbrella")[
            "id"
        ]
        a2 = shapes_mod.add_shape(s, "rectangle", 450, 280, 140, 50, "Wear sunscreen")[
            "id"
        ]
        end = shapes_mod.add_shape(s, "ellipse", 300, 400, 100, 50, "Go outside")["id"]

        conn_mod.add_connector(s, start, d1)
        conn_mod.add_connector(s, d1, a1, label="Yes")
        conn_mod.add_connector(s, d1, a2, label="No")
        conn_mod.add_connector(s, a1, end)
        conn_mod.add_connector(s, a2, end)

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)
            s2 = Session()
            proj_mod.open_project(s2, path)
            assert len(drawio_xml.get_vertices(s2.root)) == 5
            assert len(drawio_xml.get_edges(s2.root)) == 5
            print(f"\n  Decision tree: {path}")
        finally:
            os.unlink(path)

    def test_multi_page_documentation(self):
        """Build a multi-page technical document."""
        s = Session()
        proj_mod.new_project(s, "letter")
        pages_mod.rename_page(s, 0, "System Overview")

        # Page 1: High-level architecture
        shapes_mod.add_shape(s, "rectangle", 100, 100, 200, 60, "Frontend (React)")
        shapes_mod.add_shape(s, "rectangle", 100, 220, 200, 60, "Backend (Python)")
        shapes_mod.add_shape(s, "cylinder", 130, 340, 140, 80, "PostgreSQL")

        # Page 2: Deployment
        pages_mod.add_page(s, "Deployment")
        shapes_mod.add_shape(s, "cloud", 100, 50, 200, 120, "AWS", diagram_index=1)
        shapes_mod.add_shape(
            s, "rectangle", 130, 200, 140, 50, "ECS Fargate", diagram_index=1
        )
        shapes_mod.add_shape(s, "cylinder", 130, 300, 140, 80, "RDS", diagram_index=1)

        # Page 3: CI/CD
        pages_mod.add_page(s, "CI/CD Pipeline")
        shapes_mod.add_shape(
            s, "rectangle", 50, 100, 120, 50, "GitHub", diagram_index=2
        )
        shapes_mod.add_shape(
            s, "rectangle", 220, 100, 120, 50, "Actions", diagram_index=2
        )
        shapes_mod.add_shape(
            s, "rectangle", 390, 100, 120, 50, "Deploy", diagram_index=2
        )

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(s, path)

            s2 = Session()
            proj_mod.open_project(s2, path)
            pages = drawio_xml.list_pages(s2.root)
            assert len(pages) == 3
            assert pages[0]["name"] == "System Overview"
            assert pages[1]["name"] == "Deployment"
            assert pages[2]["name"] == "CI/CD Pipeline"
            print(f"\n  Multi-page doc: {path} ({len(pages)} pages)")
        finally:
            os.unlink(path)
