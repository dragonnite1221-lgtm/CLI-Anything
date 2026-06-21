# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestBlenderRenderE2E:
    """True E2E tests: generate scene → bpy script → blender --background → verify output."""

    def test_render_simple_cube(self, tmp_dir):
        """Render a simple cube scene with Blender."""
        from cli_anything.blender.utils.blender_backend import render_scene_headless

        proj = create_scene(name="simple_cube", engine="WORKBENCH", samples=1)
        set_render_settings(proj, resolution_x=320, resolution_y=240,
                           resolution_percentage=100, engine="WORKBENCH", samples=1)

        add_object(proj, mesh_type="cube", name="TestCube", location=[0, 0, 0])
        add_camera(proj, name="Cam", location=[5, -5, 3],
                   rotation=[63, 0, 46], set_active=True)
        add_light(proj, light_type="SUN", name="Sun", rotation=[-45, 0, 30])

        output_path = os.path.join(tmp_dir, "cube_render.png")
        script = generate_full_script(proj, output_path)

        result = render_scene_headless(script, output_path, timeout=120)

        assert os.path.exists(result["output"])
        assert result["file_size"] > 0
        assert result["method"] == "blender-headless"
        print(f"\n  Rendered cube: {result['output']} ({result['file_size']:,} bytes)")

    def test_render_sphere_with_material(self, tmp_dir):
        """Render a sphere with material."""
        from cli_anything.blender.utils.blender_backend import render_scene_headless

        proj = create_scene(name="material_sphere", engine="WORKBENCH", samples=1)
        set_render_settings(proj, resolution_x=320, resolution_y=240, engine="WORKBENCH", samples=1)

        add_object(proj, mesh_type="sphere", name="Ball", location=[0, 0, 0])
        create_material(proj, name="RedMetal", color=[0.8, 0.1, 0.1, 1.0],
                        metallic=0.9, roughness=0.2)
        assign_material(proj, 0, 0)

        add_camera(proj, name="Cam", location=[4, -4, 3],
                   rotation=[60, 0, 45], set_active=True)
        add_light(proj, light_type="POINT", name="Key", location=[3, -3, 5], power=500)

        output_path = os.path.join(tmp_dir, "sphere_render.png")
        script = generate_full_script(proj, output_path)

        result = render_scene_headless(script, output_path, timeout=120)

        assert os.path.exists(result["output"])
        assert result["file_size"] > 100  # Real PNG should be > 100 bytes
        print(f"\n  Rendered sphere: {result['output']} ({result['file_size']:,} bytes)")

    def test_render_complex_scene(self, tmp_dir):
        """Render a complex scene with multiple objects, materials, lights."""
        from cli_anything.blender.utils.blender_backend import render_scene_headless

        proj = create_scene(name="complex", engine="WORKBENCH", samples=1)
        set_render_settings(proj, resolution_x=320, resolution_y=240, engine="WORKBENCH", samples=1)

        # Ground plane
        add_object(proj, mesh_type="plane", name="Ground", scale=[5, 5, 1])
        create_material(proj, name="Floor", color=[0.3, 0.3, 0.3, 1], roughness=0.9)
        assign_material(proj, 0, 0)

        # Objects
        add_object(proj, mesh_type="monkey", name="Suzanne", location=[0, 0, 1])
        create_material(proj, name="Gold", color=[1.0, 0.8, 0.2, 1],
                        metallic=1.0, roughness=0.2)
        assign_material(proj, 1, 1)

        add_object(proj, mesh_type="cylinder", name="Pillar", location=[3, 0, 1])
        create_material(proj, name="Stone", color=[0.6, 0.6, 0.6, 1], roughness=0.8)
        assign_material(proj, 2, 2)

        # Camera and lights
        add_camera(proj, name="Cam", location=[7, -6, 5],
                   rotation=[63, 0, 46], focal_length=50, set_active=True)
        add_light(proj, light_type="SUN", name="Sun", rotation=[-45, 0, 30])
        add_light(proj, light_type="AREA", name="Fill", location=[-3, 3, 3], power=300)

        output_path = os.path.join(tmp_dir, "complex_render.png")
        script = generate_full_script(proj, output_path)

        result = render_scene_headless(script, output_path, timeout=180)

        assert os.path.exists(result["output"])
        assert result["file_size"] > 100
        print(f"\n  Rendered complex scene: {result['output']} ({result['file_size']:,} bytes)")

    def test_render_with_modifiers(self, tmp_dir):
        """Render an object with subdivision surface modifier."""
        from cli_anything.blender.utils.blender_backend import render_scene_headless

        proj = create_scene(name="modifiers", engine="WORKBENCH", samples=1)
        set_render_settings(proj, resolution_x=320, resolution_y=240, engine="WORKBENCH", samples=1)

        add_object(proj, mesh_type="cube", name="SmoothCube", location=[0, 0, 0])
        add_modifier(proj, "subdivision_surface", 0, params={"levels": 2, "render_levels": 2})
        create_material(proj, name="Blue", color=[0.1, 0.3, 0.8, 1])
        assign_material(proj, 0, 0)

        add_camera(proj, name="Cam", location=[4, -4, 3],
                   rotation=[60, 0, 45], set_active=True)
        add_light(proj, light_type="SUN", name="Sun")

        output_path = os.path.join(tmp_dir, "modifier_render.png")
        script = generate_full_script(proj, output_path)

        result = render_scene_headless(script, output_path, timeout=120)

        assert os.path.exists(result["output"])
        assert result["file_size"] > 100
        print(f"\n  Rendered with modifiers: {result['output']} ({result['file_size']:,} bytes)")

    def test_render_jpeg_format(self, tmp_dir):
        """Render to JPEG format."""
        from cli_anything.blender.utils.blender_backend import render_scene_headless

        proj = create_scene(name="jpeg_test", engine="WORKBENCH", samples=1)
        set_render_settings(proj, resolution_x=320, resolution_y=240,
                           engine="WORKBENCH", samples=1, output_format="JPEG")

        add_object(proj, mesh_type="sphere", name="Ball")
        add_camera(proj, name="Cam", location=[4, -4, 3],
                   rotation=[60, 0, 45], set_active=True)
        add_light(proj, light_type="SUN", name="Sun")

        output_path = os.path.join(tmp_dir, "render.jpg")
        script = generate_full_script(proj, output_path)

        result = render_scene_headless(script, output_path, timeout=120)

        assert os.path.exists(result["output"])
        assert result["file_size"] > 100
        print(f"\n  Rendered JPEG: {result['output']} ({result['file_size']:,} bytes)")
