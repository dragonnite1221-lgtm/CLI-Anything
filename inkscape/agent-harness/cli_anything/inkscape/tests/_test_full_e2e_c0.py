# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class _TestWorkflowsMixin0:
    def test_logo_design_workflow(self, tmp_dir):
        """Simulate designing a simple logo."""
        proj = create_document(name="logo", width=512, height=512, profile="icon_512")

        # Background circle
        add_circle(proj, cx=256, cy=256, r=250, name="BgCircle",
                   style="fill:#2c3e50;stroke:none")

        # Decorative elements
        add_star(proj, cx=256, cy=200, points_count=6, outer_r=80, inner_r=40,
                 name="StarDecor", style="fill:#f39c12;stroke:none")

        # Text
        add_text(proj, text="LOGO", x=256, y=350, font_size=72,
                 font_family="sans-serif", fill="#ecf0f1",
                 text_anchor="middle")

        # Apply gradient to background
        add_linear_gradient(proj, stops=[
            {"offset": 0, "color": "#2c3e50"},
            {"offset": 1, "color": "#3498db"},
        ], y1=0, y2=1)
        apply_gradient(proj, 0, 0, "fill")

        # Save both formats
        json_path = os.path.join(tmp_dir, "logo.json")
        svg_path = os.path.join(tmp_dir, "logo.svg")
        save_document(proj, json_path)
        save_svg(proj, svg_path)

        # Verify
        assert os.path.exists(json_path)
        assert os.path.exists(svg_path)
        tree = ET.parse(svg_path)
        assert tree.getroot().tag == f"{{{SVG_NS}}}svg"
    def test_infographic_workflow(self, tmp_dir):
        """Simulate creating a simple infographic."""
        proj = create_document(name="infographic", width=800, height=1200)

        # Title
        add_text(proj, text="Infographic Title", x=400, y=60,
                 font_size=36, text_anchor="middle", fill="#2c3e50")

        # Data bars
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
        values = [80, 65, 90, 45, 70]
        for i, (color, val) in enumerate(zip(colors, values)):
            y = 150 + i * 80
            # Bar background
            add_rect(proj, x=100, y=y, width=600, height=40,
                     style=f"fill:#ecf0f1;stroke:none")
            # Bar value
            bar_width = val * 6  # scale
            add_rect(proj, x=100, y=y, width=bar_width, height=40,
                     style=f"fill:{color};stroke:none")
            # Label
            add_text(proj, text=f"Item {i+1}: {val}%", x=110, y=y + 28,
                     font_size=16, fill="#ffffff")

        # Save
        svg_path = os.path.join(tmp_dir, "infographic.svg")
        save_svg(proj, svg_path)
        tree = ET.parse(svg_path)
        root = tree.getroot()
        assert root.tag == f"{{{SVG_NS}}}svg"
    def test_multi_layer_workflow(self, tmp_dir):
        """Work with multiple layers."""
        proj = create_document(name="layers_test")

        # Create layers
        add_layer(proj, name="Background")
        add_layer(proj, name="Foreground")

        # Add objects to specific layers
        add_rect(proj, name="BgFill", width=1920, height=1080,
                 style="fill:#eeeeee;stroke:none", layer=proj["layers"][1]["id"])
        add_circle(proj, cx=960, cy=540, r=100, name="MainShape",
                   layer=proj["layers"][2]["id"])

        # Verify layer structure
        layers = list_layers(proj)
        assert len(layers) == 3  # Default + 2 added

        # Save and verify
        json_path = os.path.join(tmp_dir, "layers.json")
        save_document(proj, json_path)
        loaded = open_document(json_path)
        assert len(loaded["layers"]) == 3
        assert len(loaded["objects"]) == 2
    def test_transform_workflow(self):
        """Apply multiple transforms and verify."""
        proj = create_document()
        add_rect(proj, x=0, y=0, width=100, height=100)

        translate(proj, 0, 50, 50)
        rotate(proj, 0, 45, cx=100, cy=100)
        scale(proj, 0, 1.5)

        t = get_transform(proj, 0)
        assert len(t["operations"]) == 3
        assert t["operations"][0]["type"] == "translate"
        assert t["operations"][1]["type"] == "rotate"
        assert t["operations"][2]["type"] == "scale"
