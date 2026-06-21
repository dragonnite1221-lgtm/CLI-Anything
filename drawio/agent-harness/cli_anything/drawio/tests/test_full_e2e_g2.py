# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestRealExport:
    """Test export using the real draw.io CLI.
    These tests require draw.io desktop app to be installed.
    """

    @pytest.mark.skipif(not _has_drawio(), reason="draw.io not installed")
    def test_export_png(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", 100, 100, 120, 60, "PNG Test")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            drawio_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            png_path = f.name
        os.unlink(png_path)  # draw.io needs to create it

        try:
            proj_mod.save_project(s, drawio_path)
            result = export_mod.render(s, png_path, fmt="png", overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0

            # Verify PNG magic bytes
            with open(result["output"], "rb") as f:
                header = f.read(8)
                assert header[:4] == b"\x89PNG", "Not a valid PNG file"

            print(f"\n  PNG export: {result['output']} ({result['file_size']:,} bytes)")
        finally:
            if os.path.exists(drawio_path):
                os.unlink(drawio_path)
            if os.path.exists(png_path):
                os.unlink(png_path)

    @pytest.mark.skipif(not _has_drawio(), reason="draw.io not installed")
    def test_export_svg(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "ellipse", 100, 100, 80, 80, "SVG Test")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            drawio_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            svg_path = f.name
        os.unlink(svg_path)

        try:
            proj_mod.save_project(s, drawio_path)
            result = export_mod.render(s, svg_path, fmt="svg", overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0

            # Verify SVG content
            with open(result["output"], "r") as f:
                content = f.read()
                assert "<svg" in content, "Not a valid SVG file"

            print(f"\n  SVG export: {result['output']} ({result['file_size']:,} bytes)")
        finally:
            if os.path.exists(drawio_path):
                os.unlink(drawio_path)
            if os.path.exists(svg_path):
                os.unlink(svg_path)

    @pytest.mark.skipif(not _has_drawio(), reason="draw.io not installed")
    def test_export_pdf(self):
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", 100, 100, 140, 60, "PDF Test")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            drawio_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
        os.unlink(pdf_path)

        try:
            proj_mod.save_project(s, drawio_path)
            result = export_mod.render(s, pdf_path, fmt="pdf", overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0

            # Verify PDF magic bytes
            with open(result["output"], "rb") as f:
                header = f.read(4)
                assert header == b"%PDF", "Not a valid PDF file"

            print(f"\n  PDF export: {result['output']} ({result['file_size']:,} bytes)")
        finally:
            if os.path.exists(drawio_path):
                os.unlink(drawio_path)
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
