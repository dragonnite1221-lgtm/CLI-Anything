# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestScriptValidity:
    """Verify generated bpy scripts are valid Python syntax."""

    def test_script_is_valid_python(self):
        """Ensure generated scripts parse as valid Python."""
        proj = create_scene()
        add_object(proj, mesh_type="cube", name="Test")
        add_camera(proj, name="Cam")
        add_light(proj, name="Light")
        create_material(proj, name="Mat")
        assign_material(proj, 0, 0)
        add_modifier(proj, "subdivision_surface", 0)
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])

        script = generate_full_script(proj, "/tmp/render.png")

        # Verify it parses as Python
        compile(script, "<bpy_script>", "exec")

    def test_complex_script_is_valid_python(self):
        """Ensure a complex scene generates valid Python."""
        proj = create_scene(engine="EEVEE")

        for prim in ["cube", "sphere", "cylinder", "cone", "plane", "torus", "monkey"]:
            add_object(proj, mesh_type=prim)

        for i in range(7):
            create_material(proj, name=f"Mat{i}", color=[i/7.0, 0.5, 1-i/7.0, 1.0])
            assign_material(proj, i, i)

        add_modifier(proj, "subdivision_surface", 0)
        add_modifier(proj, "mirror", 1)
        add_modifier(proj, "array", 2, params={"count": 3})
        add_modifier(proj, "bevel", 3, params={"width": 0.1})
        add_modifier(proj, "solidify", 4, params={"thickness": 0.02})
        add_modifier(proj, "boolean", 5, params={"operation": "UNION"})
        add_modifier(proj, "smooth", 6, params={"iterations": 5})

        add_camera(proj, name="Cam", set_active=True)
        add_light(proj, light_type="POINT")
        add_light(proj, light_type="SUN")
        add_light(proj, light_type="SPOT")
        add_light(proj, light_type="AREA")

        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 60, "location", [5, 0, 0])
        add_keyframe(proj, 0, 1, "rotation", [0, 0, 0])
        add_keyframe(proj, 0, 60, "rotation", [0, 0, 360])
        add_keyframe(proj, 0, 1, "scale", [1, 1, 1])
        add_keyframe(proj, 0, 60, "scale", [2, 2, 2])

        script = generate_full_script(proj, "/tmp/render.png", animation=True)
        compile(script, "<complex_bpy_script>", "exec")

    def test_animation_script_is_valid_python(self):
        proj = create_scene()
        add_object(proj, mesh_type="sphere", name="Ball")
        add_keyframe(proj, 0, 1, "location", [0, 0, 5])
        add_keyframe(proj, 0, 60, "location", [0, 0, 0])
        add_keyframe(proj, 0, 30, "visible", True)

        script = generate_full_script(proj, "/tmp/anim_", animation=True)
        compile(script, "<anim_script>", "exec")


class TestBlenderBackend:
    """Tests that verify Blender is installed and accessible."""

    def test_blender_is_installed(self):
        from cli_anything.blender.utils.blender_backend import find_blender
        path = find_blender()
        assert os.path.exists(path)
        print(f"\n  Blender binary: {path}")

    def test_blender_version(self):
        from cli_anything.blender.utils.blender_backend import get_version
        version = get_version()
        assert "Blender" in version
        print(f"\n  Blender version: {version}")
