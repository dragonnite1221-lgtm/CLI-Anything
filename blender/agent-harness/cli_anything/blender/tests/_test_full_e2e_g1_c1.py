# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowsMixin1:
    def test_modifier_stack_workflow(self, tmp_dir):
        """Build a complex modifier stack and verify it survives roundtrip."""
        proj = create_scene()
        add_object(proj, mesh_type="cube", name="Complex")

        add_modifier(proj, "subdivision_surface", 0, params={"levels": 1})
        add_modifier(proj, "bevel", 0, params={"width": 0.05, "segments": 3})
        add_modifier(proj, "array", 0, params={"count": 3, "relative_offset_x": 1.2})
        add_modifier(proj, "solidify", 0, params={"thickness": 0.02})

        assert len(proj["objects"][0]["modifiers"]) == 4

        path = os.path.join(tmp_dir, "modstack.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        mods = loaded["objects"][0]["modifiers"]
        assert len(mods) == 4
        assert mods[0]["type"] == "subdivision_surface"
        assert mods[1]["type"] == "bevel"
        assert mods[2]["type"] == "array"
        assert mods[3]["type"] == "solidify"
    def test_multi_material_workflow(self):
        """Assign different materials to multiple objects."""
        proj = create_scene()

        # Create objects
        for name in ["Cube", "Sphere", "Cone", "Cylinder"]:
            add_object(proj, mesh_type=name.lower(), name=name)

        # Create materials
        colors = {
            "Red": [1, 0, 0, 1],
            "Green": [0, 1, 0, 1],
            "Blue": [0, 0, 1, 1],
            "Yellow": [1, 1, 0, 1],
        }
        for name, color in colors.items():
            create_material(proj, name=name, color=color)

        # Assign
        for i in range(4):
            assign_material(proj, i, i)

        # Verify
        for i, obj in enumerate(proj["objects"]):
            mat_id = obj["material"]
            mat = proj["materials"][i]
            assert mat_id == mat["id"]
    def test_undo_redo_workflow(self):
        """Test undo/redo through a complex editing workflow."""
        sess = Session()
        proj = create_scene(name="undo_test")
        sess.set_project(proj)

        # Step 1: Add object
        sess.snapshot("add cube")
        add_object(proj, name="Cube")
        assert len(proj["objects"]) == 1

        # Step 2: Add material
        sess.snapshot("add material")
        create_material(proj, name="Red", color=[1, 0, 0, 1])
        assert len(proj["materials"]) == 1

        # Step 3: Modify object
        sess.snapshot("move cube")
        transform_object(proj, 0, translate=[0, 0, 3])
        assert proj["objects"][0]["location"][2] == 3.0

        # Undo step 3
        sess.undo()
        assert sess.get_project()["objects"][0]["location"][2] == 0.0

        # Undo step 2
        sess.undo()
        assert len(sess.get_project()["materials"]) == 0

        # Redo step 2
        sess.redo()
        assert len(sess.get_project()["materials"]) == 1

        # Redo step 3
        sess.redo()
        assert sess.get_project()["objects"][0]["location"][2] == 3.0
