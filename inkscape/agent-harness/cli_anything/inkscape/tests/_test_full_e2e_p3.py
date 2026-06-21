# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class TestExport:
    def test_export_svg(self, tmp_dir):
        proj = create_document()
        add_rect(proj, x=10, y=10, width=100, height=50)
        out = os.path.join(tmp_dir, "export.svg")
        result = export_svg(proj, out, overwrite=True)
        assert os.path.exists(out)
        assert result["format"] == "svg"
        assert result["size_bytes"] > 0

    def test_export_svg_overwrite_protection(self, tmp_dir):
        proj = create_document()
        out = os.path.join(tmp_dir, "existing.svg")
        with open(out, "w") as f:
            f.write("<svg/>")
        with pytest.raises(FileExistsError):
            export_svg(proj, out, overwrite=False)

    def test_export_svg_is_valid_xml(self, tmp_dir):
        proj = create_document()
        add_rect(proj)
        add_circle(proj)
        add_text(proj, text="Test")
        out = os.path.join(tmp_dir, "valid.svg")
        export_svg(proj, out, overwrite=True)
        tree = ET.parse(out)
        assert tree.getroot().tag == f"{{{SVG_NS}}}svg"

    def test_render_to_png(self, tmp_dir):
        """Test PNG rendering if Pillow is available."""
        try:
            import PIL
        except ImportError:
            pytest.skip("Pillow not installed")

        proj = create_document(width=200, height=200, background="#ffffff")
        add_rect(proj, x=10, y=10, width=80, height=80,
                 style="fill:#ff0000;stroke:#000000;stroke-width:2")
        add_circle(proj, cx=100, cy=100, r=40,
                   style="fill:#00ff00;stroke:none")

        out = os.path.join(tmp_dir, "render.png")
        result = render_to_png(proj, out, overwrite=True)
        assert os.path.exists(out)
        assert result["format"] == "png"

        # Verify it's a valid PNG
        from PIL import Image
        img = Image.open(out)
        assert img.size == (200, 200)

    def test_render_to_png_custom_size(self, tmp_dir):
        """Test PNG rendering at custom dimensions."""
        try:
            import PIL
        except ImportError:
            pytest.skip("Pillow not installed")

        proj = create_document(width=1920, height=1080)
        add_rect(proj, x=0, y=0, width=1920, height=1080,
                 style="fill:#3498db;stroke:none")

        out = os.path.join(tmp_dir, "scaled.png")
        result = render_to_png(proj, out, width=480, height=270, overwrite=True)
        assert os.path.exists(out)

        from PIL import Image
        img = Image.open(out)
        assert img.size == (480, 270)

    def test_render_to_png_overwrite_protection(self, tmp_dir):
        proj = create_document()
        out = os.path.join(tmp_dir, "existing.png")
        with open(out, "w") as f:
            f.write("fake")
        with pytest.raises(FileExistsError):
            render_to_png(proj, out, overwrite=False)

    def test_render_shapes(self, tmp_dir):
        """Test rendering multiple shape types."""
        try:
            import PIL
        except ImportError:
            pytest.skip("Pillow not installed")

        proj = create_document(width=400, height=400, background="#ffffff")
        add_rect(proj, x=10, y=10, width=80, height=60,
                 style="fill:#ff0000;stroke:#000;stroke-width:2")
        add_circle(proj, cx=200, cy=50, r=40,
                   style="fill:#00ff00;stroke:none")
        add_ellipse(proj, cx=350, cy=50, rx=40, ry=25,
                    style="fill:#0000ff;stroke:none")
        add_line(proj, x1=10, y1=200, x2=390, y2=200,
                 style="fill:none;stroke:#000;stroke-width:3")
        add_polygon(proj, points="200,250 250,350 150,350",
                    style="fill:#ff00ff;stroke:#000;stroke-width:1")
        add_text(proj, text="Shapes", x=10, y=390, font_size=24, fill="#333")

        out = os.path.join(tmp_dir, "shapes.png")
        result = render_to_png(proj, out, overwrite=True)
        assert os.path.exists(out)
        assert result["size_bytes"] > 0

    def test_render_star(self, tmp_dir):
        """Test rendering a star shape."""
        try:
            import PIL
        except ImportError:
            pytest.skip("Pillow not installed")

        proj = create_document(width=200, height=200)
        add_star(proj, cx=100, cy=100, points_count=5, outer_r=80, inner_r=30,
                 style="fill:#f1c40f;stroke:#e67e22;stroke-width:2")

        out = os.path.join(tmp_dir, "star.png")
        result = render_to_png(proj, out, overwrite=True)
        assert os.path.exists(out)
