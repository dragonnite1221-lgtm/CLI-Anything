# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import tmp_dir  # noqa: F401,E501


class _TestWorkflowsMixin1:
    def test_style_workflow(self):
        """Apply various styles and verify."""
        proj = create_document()
        add_rect(proj)

        set_fill(proj, 0, "#ff0000")
        set_stroke(proj, 0, "#000000", width=2)
        set_opacity(proj, 0, 0.8)
        set_style(proj, 0, "stroke-linejoin", "round")
        set_style(proj, 0, "stroke-dasharray", "5,3")

        style = get_object_style(proj, 0)
        assert style["fill"] == "#ff0000"
        assert style["stroke"] == "#000000"
        assert style["stroke-width"] == "2"
        assert style["opacity"] == "0.8"
        assert style["stroke-linejoin"] == "round"
        assert style["stroke-dasharray"] == "5,3"
    def test_path_operations_workflow(self):
        """Test path boolean operations."""
        proj = create_document()
        add_rect(proj, x=0, y=0, width=100, height=100, name="Square")
        add_circle(proj, cx=80, cy=50, r=50, name="Circle")

        result = path_union(proj, 0, 1, name="Combined")
        assert result["type"] == "path"
        assert result["boolean_operation"]["type"] == "union"
        assert len(proj["objects"]) == 1
    def test_undo_redo_workflow(self):
        """Test undo/redo through a complex editing workflow."""
        sess = Session()
        proj = create_document(name="undo_test")
        sess.set_project(proj)

        # Step 1: Add rect
        sess.snapshot("add rect")
        add_rect(proj, name="Rect")
        assert len(proj["objects"]) == 1

        # Step 2: Add circle
        sess.snapshot("add circle")
        add_circle(proj, name="Circle")
        assert len(proj["objects"]) == 2

        # Step 3: Style change
        sess.snapshot("change style")
        set_fill(proj, 0, "#ff0000")
        style = get_object_style(proj, 0)
        assert style["fill"] == "#ff0000"

        # Undo style change
        sess.undo()
        proj = sess.get_project()
        style = get_object_style(proj, 0)
        assert style["fill"] != "#ff0000"

        # Undo circle add
        sess.undo()
        proj = sess.get_project()
        assert len(proj["objects"]) == 1

        # Redo circle add
        sess.redo()
        proj = sess.get_project()
        assert len(proj["objects"]) == 2
    def test_gradient_workflow(self, tmp_dir):
        """Create and apply gradients, then export."""
        proj = create_document(width=400, height=400)

        # Create gradient
        add_linear_gradient(proj, stops=[
            {"offset": 0, "color": "#ff0000"},
            {"offset": 0.5, "color": "#00ff00"},
            {"offset": 1, "color": "#0000ff"},
        ], name="Rainbow")

        # Create shape and apply gradient
        add_rect(proj, x=50, y=50, width=300, height=300, name="GradBox")
        apply_gradient(proj, 0, 0, "fill")

        # Export SVG
        svg_path = os.path.join(tmp_dir, "gradient.svg")
        save_svg(proj, svg_path)
        tree = ET.parse(svg_path)
        defs = tree.getroot().find(f"{{{SVG_NS}}}defs")
        grads = list(defs.iter(f"{{{SVG_NS}}}linearGradient"))
        assert len(grads) >= 1
        stops = list(grads[0].iter(f"{{{SVG_NS}}}stop"))
        assert len(stops) == 3
