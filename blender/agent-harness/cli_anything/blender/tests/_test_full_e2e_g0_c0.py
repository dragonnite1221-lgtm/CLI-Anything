# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestBPYScriptGenerationMixin0:
    def test_empty_scene_script(self):
        proj = create_scene(name="empty")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "import bpy" in script
        assert "bpy.ops.object.select_all" in script
        assert "scene.render.engine" in script
    def test_script_contains_objects(self):
        proj = create_scene()
        add_object(proj, mesh_type="cube", name="TestCube", location=[1, 2, 3])
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_cube_add" in script
        assert "TestCube" in script
        assert "1, 2, 3" in script
    def test_script_contains_sphere(self):
        proj = create_scene()
        add_object(proj, mesh_type="sphere", mesh_params={"radius": 2.0, "segments": 64})
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_uv_sphere_add" in script
        assert "radius=2.0" in script
        assert "segments=64" in script
    def test_script_contains_cylinder(self):
        proj = create_scene()
        add_object(proj, mesh_type="cylinder")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_cylinder_add" in script
    def test_script_contains_cone(self):
        proj = create_scene()
        add_object(proj, mesh_type="cone")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_cone_add" in script
    def test_script_contains_plane(self):
        proj = create_scene()
        add_object(proj, mesh_type="plane")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_plane_add" in script
    def test_script_contains_torus(self):
        proj = create_scene()
        add_object(proj, mesh_type="torus")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_torus_add" in script
    def test_script_contains_monkey(self):
        proj = create_scene()
        add_object(proj, mesh_type="monkey")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "primitive_monkey_add" in script
    def test_script_contains_materials(self):
        proj = create_scene()
        create_material(proj, name="TestMat", color=[1, 0, 0, 1], metallic=0.8)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "bpy.data.materials.new" in script
        assert "TestMat" in script
        assert "Metallic" in script
    def test_script_contains_modifiers(self):
        proj = create_scene()
        add_object(proj, name="Cube")
        add_modifier(proj, "subdivision_surface", 0, params={"levels": 2, "render_levels": 3})
        script = generate_full_script(proj, "/tmp/render.png")
        assert "modifiers.new" in script
        assert "SUBSURF" in script
        assert "mod.levels = 2" in script
        assert "mod.render_levels = 3" in script
    def test_script_contains_mirror_modifier(self):
        proj = create_scene()
        add_object(proj, name="Cube")
        add_modifier(proj, "mirror", 0)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "MIRROR" in script
        assert "use_axis" in script
    def test_script_contains_array_modifier(self):
        proj = create_scene()
        add_object(proj, name="Cube")
        add_modifier(proj, "array", 0, params={"count": 5})
        script = generate_full_script(proj, "/tmp/render.png")
        assert "ARRAY" in script
        assert "mod.count = 5" in script
    def test_script_contains_cameras(self):
        proj = create_scene()
        add_camera(proj, name="RenderCam", location=[7, -6, 5], focal_length=85)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "bpy.data.cameras.new" in script
        assert "RenderCam" in script
        assert "cam_data.lens = 85" in script
    def test_script_contains_lights(self):
        proj = create_scene()
        add_light(proj, light_type="SUN", name="Sun", power=2.0)
        script = generate_full_script(proj, "/tmp/render.png")
        assert "bpy.data.lights.new" in script
        assert "SUN" in script
        assert "energy = 2.0" in script
    def test_script_contains_spot_light(self):
        proj = create_scene()
        add_light(proj, light_type="SPOT")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "SPOT" in script
        assert "spot_size" in script
    def test_script_contains_area_light(self):
        proj = create_scene()
        add_light(proj, light_type="AREA")
        script = generate_full_script(proj, "/tmp/render.png")
        assert "AREA" in script
        assert "light_data.size" in script
    def test_script_contains_keyframes(self):
        proj = create_scene()
        add_object(proj, name="Animated")
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 60, "location", [5, 0, 0])
        script = generate_full_script(proj, "/tmp/render.png")
        assert "keyframe_insert" in script
        assert "location" in script
