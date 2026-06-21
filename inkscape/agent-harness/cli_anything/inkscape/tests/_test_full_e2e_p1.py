# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class TestSVGValidity:
    """Verify that generated SVG is well-formed XML with correct namespaces."""

    def test_empty_document_svg_is_valid_xml(self, tmp_dir):
        proj = create_document(name="empty")
        path = os.path.join(tmp_dir, "empty.svg")
        save_svg(proj, path)
        # Parse it back — will raise if invalid XML
        tree = ET.parse(path)
        root = tree.getroot()
        assert root.tag == f"{{{SVG_NS}}}svg"

    def test_svg_has_xml_declaration(self, tmp_dir):
        proj = create_document()
        path = os.path.join(tmp_dir, "test.svg")
        save_svg(proj, path)
        with open(path) as f:
            content = f.read()
        assert content.startswith("<?xml")

    def test_svg_has_correct_dimensions(self, tmp_dir):
        proj = create_document(width=800, height=600)
        path = os.path.join(tmp_dir, "test.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        root = tree.getroot()
        assert "800" in root.get("width", "")
        assert "600" in root.get("height", "")

    def test_svg_has_viewbox(self, tmp_dir):
        proj = create_document(width=1920, height=1080)
        path = os.path.join(tmp_dir, "test.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        root = tree.getroot()
        assert root.get("viewBox") == "0 0 1920 1080"

    def test_svg_has_inkscape_namespace(self, tmp_dir):
        proj = create_document()
        svg = project_to_svg(proj)
        xml_str = serialize_svg(svg)
        assert "inkscape" in xml_str

    def test_svg_with_shapes_is_valid(self, tmp_dir):
        proj = create_document()
        add_rect(proj, x=10, y=10, width=100, height=50)
        add_circle(proj, cx=200, cy=200, r=30)
        add_ellipse(proj, cx=300, cy=100, rx=60, ry=30)
        path = os.path.join(tmp_dir, "shapes.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        root = tree.getroot()
        # Should have layer group and shapes inside
        groups = list(root.iter(f"{{{SVG_NS}}}g"))
        assert len(groups) >= 1  # At least the layer group

    def test_svg_with_text_is_valid(self, tmp_dir):
        proj = create_document()
        add_text(proj, text="Hello SVG", x=50, y=100, font_size=48)
        path = os.path.join(tmp_dir, "text.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        # Find text element
        texts = list(tree.getroot().iter(f"{{{SVG_NS}}}text"))
        assert len(texts) >= 1
        assert texts[0].text == "Hello SVG"

    def test_svg_with_gradients_is_valid(self, tmp_dir):
        proj = create_document()
        add_linear_gradient(proj, stops=[
            {"offset": 0, "color": "#ff0000"},
            {"offset": 1, "color": "#0000ff"},
        ])
        add_rect(proj, name="GradRect")
        apply_gradient(proj, 0, 0, "fill")
        path = os.path.join(tmp_dir, "gradient.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        defs = tree.getroot().find(f"{{{SVG_NS}}}defs")
        grads = list(defs.iter(f"{{{SVG_NS}}}linearGradient"))
        assert len(grads) >= 1
        stops = list(grads[0].iter(f"{{{SVG_NS}}}stop"))
        assert len(stops) == 2

    def test_svg_with_layers_is_valid(self, tmp_dir):
        proj = create_document()
        add_layer(proj, name="Foreground")
        add_rect(proj, name="BgRect")
        add_rect(proj, name="FgRect", layer=proj["layers"][1]["id"])
        path = os.path.join(tmp_dir, "layers.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        root = tree.getroot()
        groups = list(root.iter(f"{{{SVG_NS}}}g"))
        # Should have at least 2 layer groups
        assert len(groups) >= 2

    def test_svg_with_transform_is_valid(self, tmp_dir):
        proj = create_document()
        add_rect(proj)
        translate(proj, 0, 50, 50)
        rotate(proj, 0, 45)
        path = os.path.join(tmp_dir, "transform.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        rects = list(tree.getroot().iter(f"{{{SVG_NS}}}rect"))
        # Find rect with transform (skip background)
        transformed = [r for r in rects if r.get("transform")]
        assert len(transformed) >= 1
        assert "translate" in transformed[0].get("transform", "")

    def test_svg_radial_gradient(self, tmp_dir):
        proj = create_document()
        add_radial_gradient(proj, cx=0.5, cy=0.5, r=0.5)
        add_circle(proj)
        apply_gradient(proj, 0, 0, "fill")
        path = os.path.join(tmp_dir, "radial.svg")
        save_svg(proj, path)
        tree = ET.parse(path)
        defs = tree.getroot().find(f"{{{SVG_NS}}}defs")
        grads = list(defs.iter(f"{{{SVG_NS}}}radialGradient"))
        assert len(grads) >= 1
