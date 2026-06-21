# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class _TestWorkflowsMixin2:
    def test_full_document_export(self, tmp_dir):
        """Full workflow: create, edit, export to all formats."""
        proj = create_document(name="full", width=800, height=600)

        # Add various elements
        add_rect(proj, x=0, y=0, width=800, height=600,
                 style="fill:#f0f0f0;stroke:none")
        add_circle(proj, cx=400, cy=300, r=100,
                   style="fill:#3498db;stroke:#2980b9;stroke-width:3")
        add_text(proj, text="Full Export Test", x=400, y=50,
                 font_size=32, text_anchor="middle")

        # Export SVG
        svg_path = os.path.join(tmp_dir, "full.svg")
        result = export_svg(proj, svg_path, overwrite=True)
        assert os.path.exists(svg_path)

        # Export JSON
        json_path = os.path.join(tmp_dir, "full.json")
        save_document(proj, json_path)
        assert os.path.exists(json_path)

        # Export PNG (if Pillow available)
        try:
            import PIL
            png_path = os.path.join(tmp_dir, "full.png")
            result = render_to_png(proj, png_path, overwrite=True)
            assert os.path.exists(png_path)
        except ImportError:
            pass
