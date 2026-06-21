# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class TestInkscapeBackend:
    """Tests that verify Inkscape is installed and accessible."""

    def test_inkscape_is_installed(self):
        from cli_anything.inkscape.utils.inkscape_backend import find_inkscape
        path = find_inkscape()
        assert os.path.exists(path)
        print(f"\n  Inkscape binary: {path}")

    def test_inkscape_version(self):
        from cli_anything.inkscape.utils.inkscape_backend import get_version
        version = get_version()
        assert "Inkscape" in version
        print(f"\n  Inkscape version: {version}")


class TestInkscapeExportE2E:
    """True E2E tests: create SVG → Inkscape export → verify output."""

    def test_svg_to_png(self):
        """Export SVG to PNG using Inkscape."""
        from cli_anything.inkscape.utils.inkscape_backend import export_svg_to_png

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a simple SVG
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150">
  <rect width="200" height="150" fill="#3498db"/>
  <circle cx="100" cy="75" r="50" fill="#e74c3c"/>
  <text x="100" y="80" text-anchor="middle" fill="white" font-size="20">Test</text>
</svg>'''
            svg_path = os.path.join(tmp_dir, "test.svg")
            with open(svg_path, 'w') as f:
                f.write(svg_content)

            png_path = os.path.join(tmp_dir, "test.png")
            result = export_svg_to_png(svg_path, png_path, dpi=96, overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            assert result["method"] == "inkscape"
            print(f"\n  SVG→PNG: {result['output']} ({result['file_size']:,} bytes)")

    def test_svg_to_pdf(self):
        """Export SVG to PDF using Inkscape."""
        from cli_anything.inkscape.utils.inkscape_backend import export_svg_to_pdf

        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150">
  <rect width="200" height="150" fill="#2ecc71"/>
  <text x="100" y="80" text-anchor="middle" fill="white" font-size="24">PDF Test</text>
</svg>'''
            svg_path = os.path.join(tmp_dir, "test.svg")
            with open(svg_path, 'w') as f:
                f.write(svg_content)

            pdf_path = os.path.join(tmp_dir, "test.pdf")
            result = export_svg_to_pdf(svg_path, pdf_path, overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            # Verify PDF magic bytes
            with open(result["output"], "rb") as f:
                magic = f.read(5)
            assert magic == b"%PDF-", f"Not a valid PDF: {magic}"
            print(f"\n  SVG→PDF: {result['output']} ({result['file_size']:,} bytes)")

    def test_svg_to_png_with_dimensions(self):
        """Export SVG to PNG with specific dimensions."""
        from cli_anything.inkscape.utils.inkscape_backend import export_svg_to_png

        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_content = '''<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect width="100" height="100" fill="purple"/>
</svg>'''
            svg_path = os.path.join(tmp_dir, "small.svg")
            with open(svg_path, 'w') as f:
                f.write(svg_content)

            png_path = os.path.join(tmp_dir, "large.png")
            result = export_svg_to_png(svg_path, png_path, width=400, height=400, overwrite=True)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  SVG→PNG (400x400): {result['output']} ({result['file_size']:,} bytes)")
