# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class TestDocumentLifecycle:
    def test_create_save_open_roundtrip(self, tmp_dir):
        proj = create_document(name="roundtrip")
        path = os.path.join(tmp_dir, "doc.inkscape-cli.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert loaded["name"] == "roundtrip"
        assert loaded["document"]["width"] == 1920

    def test_document_with_objects_roundtrip(self, tmp_dir):
        proj = create_document(name="with_objects")
        add_rect(proj, name="MyRect", x=10, y=20, width=200, height=100)
        add_circle(proj, name="MyCircle", cx=300, cy=300, r=50)
        path = os.path.join(tmp_dir, "doc.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert len(loaded["objects"]) == 2
        assert loaded["objects"][0]["type"] == "rect"
        assert loaded["objects"][1]["type"] == "circle"

    def test_document_with_styles_roundtrip(self, tmp_dir):
        proj = create_document()
        add_rect(proj)
        set_fill(proj, 0, "#ff0000")
        set_stroke(proj, 0, "#000000", width=3)
        set_opacity(proj, 0, 0.8)
        path = os.path.join(tmp_dir, "styled.json")
        save_document(proj, path)
        loaded = open_document(path)
        style = get_object_style(loaded, 0)
        assert style["fill"] == "#ff0000"
        assert style["stroke"] == "#000000"

    def test_document_with_layers_roundtrip(self, tmp_dir):
        proj = create_document()
        add_layer(proj, name="Layer 2")
        add_rect(proj, name="Shape1")
        add_rect(proj, name="Shape2", layer=proj["layers"][1]["id"])
        path = os.path.join(tmp_dir, "layered.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert len(loaded["layers"]) == 2
        assert len(loaded["objects"]) == 2

    def test_document_with_gradients_roundtrip(self, tmp_dir):
        proj = create_document()
        add_linear_gradient(proj, name="MyGrad", stops=[
            {"offset": 0, "color": "#ff0000"},
            {"offset": 1, "color": "#0000ff"},
        ])
        path = os.path.join(tmp_dir, "grads.json")
        save_document(proj, path)
        loaded = open_document(path)
        assert len(loaded["gradients"]) == 1
        assert loaded["gradients"][0]["name"] == "MyGrad"

    def test_document_info_complete(self):
        proj = create_document(name="info_test")
        add_rect(proj)
        add_circle(proj)
        add_text(proj, text="Hello")
        add_layer(proj, name="Extra")
        add_linear_gradient(proj)
        info = get_document_info(proj)
        assert info["counts"]["objects"] == 3
        assert info["counts"]["layers"] == 2
        assert info["counts"]["gradients"] == 1

    def test_complex_document_roundtrip(self, tmp_dir):
        """Create a complex document, save, reload, verify."""
        proj = create_document(name="complex", width=1920, height=1080)

        # Shapes
        add_rect(proj, x=0, y=0, width=1920, height=1080, name="Background",
                 style="fill:#f0f0f0;stroke:none")
        add_rect(proj, x=100, y=100, width=400, height=300, rx=20, ry=20,
                 name="Card", style="fill:#ffffff;stroke:#cccccc;stroke-width:1")
        add_circle(proj, cx=960, cy=540, r=200, name="MainCircle",
                   style="fill:#3498db;stroke:none")
        add_ellipse(proj, cx=500, cy=800, rx=150, ry=80, name="Shadow",
                    style="fill:#00000033;stroke:none")
        add_line(proj, x1=100, y1=500, x2=1820, y2=500, name="Divider")
        add_star(proj, cx=1500, cy=200, points_count=5, outer_r=100, inner_r=40,
                 name="Star", style="fill:#f1c40f;stroke:#e67e22;stroke-width:2")
        add_polygon(proj, points="960,50 1050,350 750,350", name="Triangle",
                    style="fill:#e74c3c;stroke:none")

        # Text
        add_text(proj, text="Inkscape CLI Demo", x=100, y=50, font_size=36,
                 font_family="sans-serif", fill="#333333")

        # Styles
        set_opacity(proj, 3, 0.5)  # Shadow at half opacity

        # Transforms
        translate(proj, 2, 0, -20)  # Lift main circle
        rotate(proj, 5, 15, cx=1500, cy=200)  # Rotate star

        # Layers
        add_layer(proj, name="Foreground")

        # Gradients
        add_linear_gradient(proj, stops=[
            {"offset": 0, "color": "#3498db"},
            {"offset": 1, "color": "#2ecc71"},
        ], name="BlueGreen")
        apply_gradient(proj, 2, 0, "fill")  # Apply to MainCircle

        # Save JSON and SVG
        json_path = os.path.join(tmp_dir, "complex.json")
        svg_path = os.path.join(tmp_dir, "complex.svg")
        save_document(proj, json_path)
        save_svg(proj, svg_path)

        # Verify JSON roundtrip
        loaded = open_document(json_path)
        assert len(loaded["objects"]) == 8
        assert len(loaded["layers"]) == 2
        assert len(loaded["gradients"]) == 1

        # Verify SVG is valid XML
        tree = ET.parse(svg_path)
        root = tree.getroot()
        assert root.tag == f"{{{SVG_NS}}}svg"

    def test_svg_and_json_stay_in_sync(self, tmp_dir):
        """Verify that both JSON and SVG reflect the same state."""
        proj = create_document(width=800, height=600)
        add_rect(proj, x=10, y=10, width=100, height=50, name="R1")
        add_circle(proj, cx=200, cy=200, r=30, name="C1")

        json_path = os.path.join(tmp_dir, "sync.json")
        svg_path = os.path.join(tmp_dir, "sync.svg")
        save_document(proj, json_path)
        save_svg(proj, svg_path)

        # Both files should exist
        assert os.path.exists(json_path)
        assert os.path.exists(svg_path)

        # JSON has 2 objects
        loaded = open_document(json_path)
        assert len(loaded["objects"]) == 2

        # SVG has shapes (rect for bg + 2 shapes)
        tree = ET.parse(svg_path)
        rects = list(tree.getroot().iter(f"{{{SVG_NS}}}rect"))
        circles = list(tree.getroot().iter(f"{{{SVG_NS}}}circle"))
        assert len(rects) >= 2  # background + R1
        assert len(circles) >= 1
