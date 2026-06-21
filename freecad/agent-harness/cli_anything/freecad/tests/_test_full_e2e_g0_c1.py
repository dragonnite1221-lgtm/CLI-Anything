# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestIntermediateFilesMixin1:
    def test_macro_generation_syntax(self, tmp_path):
        """Generate a macro and verify it is valid Python via ast.parse."""
        proj = create_document(name="MacroTest")
        add_part(proj, "box", name="TestBox", params={"length": 15, "width": 10, "height": 5})
        add_part(proj, "cylinder", name="TestCyl", params={"radius": 3, "height": 20})
        add_part(proj, "sphere", name="TestSphere", params={"radius": 7})

        # Create body with features
        create_sketch(proj, plane="XY")
        add_rectangle(proj, 0, corner=[0, 0], width=10, height=10)
        create_body(proj, name="ExtrudedBody")
        pad(proj, 0, 0, length=10)

        output_path = str(tmp_path / "output.step")
        macro = generate_macro(proj, output_path, export_format="step")

        # Must be non-empty
        assert len(macro) > 100, f"Macro too short: {len(macro)} chars"

        # Must be valid Python syntax
        try:
            ast.parse(macro)
        except SyntaxError as exc:
            pytest.fail(f"Generated macro has invalid Python syntax: {exc}\n\n{macro}")

        # Must contain key FreeCAD imports
        assert "import FreeCAD" in macro
        assert "import Part" in macro
        assert "doc.recompute()" in macro

        # Should reference our parts
        assert "TestBox" in macro
        assert "TestCyl" in macro
        assert "TestSphere" in macro

        # Save macro for inspection
        macro_path = str(tmp_path / "macro.py")
        with open(macro_path, "w", encoding="utf-8") as f:
            f.write(macro)

        print(f"\n  Macro: {macro_path} ({len(macro):,} chars, {macro.count(chr(10))} lines)")
    def test_macro_generation_body_primitives_and_patterns(self, tmp_path):
        """Generate a macro containing body primitive placements and pattern features."""
        proj = create_document(name="MacroBodyTower")
        create_body(proj, name="TowerBody")
        additive_box(
            proj,
            0,
            length=36,
            width=36,
            height=18,
            position=[0, 0, 0],
        )
        additive_box(
            proj,
            0,
            length=8,
            width=6,
            height=4,
            position=[22, 0, 8],
        )
        polar_pattern(proj, 0, axis="Z", angle=360, occurrences=4)
        additive_cylinder(proj, 0, radius=2.0, height=16, position=[0, 0, 18])
        linear_pattern(proj, 0, direction=[0, 0, 1], length=48, occurrences=3)
        additive_cone(proj, 0, radius1=3, radius2=0.6, height=10, position=[0, 0, 70])

        macro = generate_macro(proj, str(tmp_path / "tower.step"))
        ast.parse(macro)

        assert "PartDesign::AdditiveBox" in macro
        assert "PartDesign::PolarPattern" in macro
        assert "PartDesign::LinearPattern" in macro
        assert "Placement = FreeCAD.Placement" in macro
        assert "_body_origin_ref" in macro
    def test_macro_generation_mirror_part_rendering(self, tmp_path):
        """Generate a macro that reconstructs mirrored primitive parts for preview/export."""
        proj = create_document(name="MirrorPreview")
        add_part(
            proj,
            "cylinder",
            name="LeftWheel",
            params={"radius": 12, "height": 6},
            position=[24, -20, 12],
            rotation=[90, 0, 0],
        )
        mirror_part(proj, 0, plane="XZ", name="RightWheel")

        macro = generate_macro(proj, str(tmp_path / "mirror.step"))
        ast.parse(macro)

        assert "obj_RightWheel = doc.addObject('Part::Cylinder', 'RightWheel')" in macro
        assert "Unknown part type 'mirror'" not in macro
        assert "obj_RightWheel.Placement = FreeCAD.Placement(FreeCAD.Vector(24.0, 20.0, 12.0)" in macro
