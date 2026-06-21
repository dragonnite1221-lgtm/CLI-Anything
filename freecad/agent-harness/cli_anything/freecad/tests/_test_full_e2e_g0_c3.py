# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestIntermediateFilesMixin3:
    def test_complex_workflow(self, tmp_path):
        """Full pipeline: document -> parts -> sketch -> body -> materials."""
        # 1. Create document
        proj = create_document(name="ComplexWorkflow", profile="print3d")
        assert proj["units"] == "mm"

        # 2. Add multiple parts
        box = add_part(proj, "box", name="Platform",
                       params={"length": 50, "width": 50, "height": 5})
        cyl = add_part(proj, "cylinder", name="Pillar",
                       params={"radius": 5, "height": 40},
                       position=[25, 25, 5])
        sphere = add_part(proj, "sphere", name="Top",
                          params={"radius": 8},
                          position=[25, 25, 45])

        # 3. Transform a part
        transform_part(proj, 2, position=[25, 25, 50], rotation=[0, 0, 45])
        top = get_part(proj, 2)
        assert top["placement"]["position"] == [25.0, 25.0, 50.0]
        assert top["placement"]["rotation"] == [0.0, 0.0, 45.0]

        # 4. Boolean fuse
        fuse_result = boolean_op(proj, "fuse", 0, 1, name="PlatformPillar")
        assert fuse_result["type"] == "fuse"
        assert len(list_parts(proj)) == 4  # box, cyl, sphere, fuse

        # 5. Create sketch with various elements
        sk = create_sketch(proj, name="DetailSketch", plane="XY", offset=5.0)
        assert sk["plane"] == "XY"
        assert sk["offset"] == 5.0

        add_rectangle(proj, 0, corner=[10, 10], width=30, height=30)
        add_circle(proj, 0, center=[25, 25], radius=10)
        add_arc(proj, 0, center=[25, 25], radius=15, start_angle=0, end_angle=180)

        # Add a constraint
        sketch_data = proj["sketches"][0]
        line_ids = [el["id"] for el in sketch_data["elements"] if el["type"] == "line"]
        assert len(line_ids) >= 2, "Should have at least 2 lines from rectangle"
        add_constraint(proj, 0, "horizontal", [line_ids[0]])

        # Close the sketch
        closed = close_sketch(proj, 0)
        assert closed["closed"] is True

        sketches = list_sketches(proj)
        assert len(sketches) == 1
        assert sketches[0]["closed"] is True
        assert sketches[0]["element_count"] >= 6  # 4 rect lines + circle + arc

        # 6. Create body with features
        body = create_body(proj, name="DetailBody")
        # Create a new open sketch for the body
        create_sketch(proj, name="BodySketch", plane="XY")
        add_rectangle(proj, 1, corner=[0, 0], width=20, height=20)

        pad_feat = pad(proj, 0, 1, length=20)
        assert pad_feat["type"] == "pad"
        assert pad_feat["length"] == 20.0

        fillet_feat = fillet(proj, 0, radius=2.0)
        assert fillet_feat["type"] == "fillet"
        assert fillet_feat["radius"] == 2.0

        bodies = list_bodies(proj)
        assert len(bodies) == 1
        assert bodies[0]["feature_count"] == 2

        # 7. Materials
        steel = create_material(proj, preset="steel")
        copper = create_material(proj, preset="copper")
        assert steel["preset"] == "steel"
        assert copper["preset"] == "copper"

        assign_material(proj, 0, 0)  # steel -> Platform(box)
        assign_material(proj, 1, 1)  # copper -> Pillar(cylinder)

        mats = list_materials(proj)
        assert len(mats) == 2
        assert 0 in mats[0]["assigned_to"]
        assert 1 in mats[1]["assigned_to"]

        # 8. Save and verify
        path = str(tmp_path / "complex.json")
        saved = save_document(proj, path)
        assert os.path.isfile(saved)

        info = get_document_info(proj)
        assert info["parts_count"] == 4
        assert info["sketches_count"] == 2
        assert info["bodies_count"] == 1
        assert info["materials_count"] == 2

        # 9. Generate macro
        macro = generate_macro(proj, str(tmp_path / "complex.step"))
        ast.parse(macro)  # valid Python

        # 10. Export info
        exp_info = get_export_info(proj)
        assert exp_info["part_count"] == 4
        assert "Platform" in exp_info["part_names"]

        print(f"\n  Complex workflow: {path} ({os.path.getsize(path):,} bytes)")
        print(f"  Parts: {info['parts_count']}, Sketches: {info['sketches_count']}, "
              f"Bodies: {info['bodies_count']}, Materials: {info['materials_count']}")
