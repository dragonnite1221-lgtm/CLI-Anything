# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestBPYScriptGenerationMixin1:
    def test_script_render_settings_cycles(self):
        proj = create_scene(engine="CYCLES", samples=256)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "CYCLES" in script
        assert "scene.cycles.samples = 256" in script
    def test_script_render_settings_eevee(self):
        proj = create_scene(engine="EEVEE", samples=64)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "BLENDER_EEVEE_NEXT" in script
        assert "eevee.taa_render_samples" in script
    def test_script_world_settings(self):
        proj = create_scene()
        script = generate_full_script(proj, "/tmp/render.png")
        assert "bpy.data.worlds" in script
        assert "Background" in script
    def test_script_render_still(self):
        proj = create_scene()
        script = generate_full_script(proj, "/tmp/render.png", frame=10)
        assert "frame_set(10)" in script
        assert "render.render(write_still=True)" in script
    def test_script_render_animation(self):
        proj = create_scene()
        script = generate_full_script(proj, "/tmp/render_", animation=True)
        assert "render.render(animation=True)" in script
    def test_script_output_format(self):
        proj = create_scene()
        proj["render"]["output_format"] = "JPEG"
        script = generate_full_script(proj, "/tmp/render.jpg")
        assert "JPEG" in script
    def test_script_material_assignment(self):
        proj = create_scene()
        mat = create_material(proj, name="Red", color=[1, 0, 0, 1])
        add_object(proj, name="Cube")
        assign_material(proj, 0, 0)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "materials.append" in script
    def test_script_contains_parenting(self):
        proj = create_scene()
        parent = add_object(proj, mesh_type="empty", name="RigRoot")
        add_object(proj, name="ChildCube")
        proj["objects"][1]["parent"] = parent["id"]
        script = generate_full_script(proj, "/tmp/render.png")
        assert "child_obj.parent = parent_obj" in script
        assert "matrix_parent_inverse" in script
    def test_render_scene_creates_script_file(self, tmp_dir):
        proj = create_scene()
        add_object(proj, name="Cube")
        output_path = os.path.join(tmp_dir, "render.png")
        result = render_scene(proj, output_path, overwrite=True)
        assert os.path.exists(result["script_path"])
        with open(result["script_path"]) as f:
            content = f.read()
        assert "import bpy" in content
    def test_script_handles_hidden_objects(self):
        proj = create_scene()
        obj = add_object(proj, name="Hidden")
        obj["visible"] = False
        script = generate_full_script(proj, "/tmp/render.png")
        assert "hide_render = True" in script
    def test_script_handles_dof(self):
        proj = create_scene()
        cam = add_camera(proj, name="DOFCam")
        cam["dof_enabled"] = True
        cam["dof_focus_distance"] = 5.0
        cam["dof_aperture"] = 1.4
        script = generate_full_script(proj, "/tmp/render.png")
        assert "dof.use_dof = True" in script
        assert "focus_distance = 5.0" in script
