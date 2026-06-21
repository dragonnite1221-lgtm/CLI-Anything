# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowsMixin0:
    def test_product_render_workflow(self, tmp_dir):
        """Simulate a product render: object + material + lighting + camera."""
        proj = create_scene(name="product", profile="product_render")

        # Ground plane
        add_object(proj, mesh_type="plane", name="Ground", scale=[5, 5, 1])
        create_material(proj, name="Floor", color=[0.9, 0.9, 0.9, 1], roughness=0.8)
        assign_material(proj, 0, 0)

        # Product object
        add_object(proj, mesh_type="monkey", name="Product", location=[0, 0, 0.8])
        add_modifier(proj, "subdivision_surface", 1, params={"levels": 2, "render_levels": 3})
        create_material(proj, name="ProductMat", color=[0.8, 0.2, 0.1, 1],
                        metallic=0.3, roughness=0.4)
        assign_material(proj, 1, 1)

        # Lighting
        add_light(proj, light_type="AREA", name="KeyLight", location=[3, -3, 5],
                  rotation=[-45, 0, 45], power=1000)
        add_light(proj, light_type="AREA", name="FillLight", location=[-3, 2, 4],
                  power=300)
        add_light(proj, light_type="AREA", name="RimLight", location=[0, 5, 3],
                  power=500)

        # Camera
        add_camera(proj, name="ProductCam", location=[5, -5, 3],
                   rotation=[63, 0, 46], focal_length=85, set_active=True)

        # Render settings
        set_render_settings(proj, engine="CYCLES", samples=256)

        # Generate script
        output_path = os.path.join(tmp_dir, "product.png")
        result = render_scene(proj, output_path, overwrite=True)
        assert os.path.exists(result["script_path"])
        assert result["engine"] == "CYCLES"
    def test_animation_workflow(self, tmp_dir):
        """Simulate an animation workflow with keyframes."""
        proj = create_scene(name="turntable", fps=30)

        # Object
        add_object(proj, mesh_type="monkey", name="Suzanne")
        add_modifier(proj, "subdivision_surface", 0, params={"levels": 2})
        create_material(proj, name="Gold", color=[1.0, 0.8, 0.2, 1],
                        metallic=1.0, roughness=0.2)
        assign_material(proj, 0, 0)

        # Keyframes: 360 turntable
        set_frame_range(proj, 1, 120)
        add_keyframe(proj, 0, 1, "rotation", [0, 0, 0])
        add_keyframe(proj, 0, 120, "rotation", [0, 0, 360])

        # Camera
        add_camera(proj, name="Turntable Cam", location=[5, 0, 2],
                   rotation=[75, 0, 90], set_active=True)

        # Light
        add_light(proj, light_type="SUN", name="Sun", rotation=[-45, 0, 30])

        # Generate animation render
        output_path = os.path.join(tmp_dir, "frame_")
        result = render_scene(proj, output_path, animation=True, overwrite=True)
        assert result["animation"] is True
        assert "1-120" in result["frame_range"]
    def test_architectural_workflow(self, tmp_dir):
        """Simulate an architectural visualization."""
        proj = create_scene(name="arch_viz", engine="CYCLES", samples=512)

        # Floor
        add_object(proj, mesh_type="plane", name="Floor", scale=[20, 20, 1])
        create_material(proj, name="Concrete", color=[0.6, 0.58, 0.55, 1], roughness=0.9)
        assign_material(proj, 0, 0)

        # Walls (cubes scaled flat)
        add_object(proj, mesh_type="cube", name="WallBack",
                   location=[0, 10, 1.5], scale=[10, 0.15, 1.5])
        add_object(proj, mesh_type="cube", name="WallLeft",
                   location=[-10, 0, 1.5], scale=[0.15, 10, 1.5])

        # Furniture
        add_object(proj, mesh_type="cube", name="Table",
                   location=[0, 0, 0.4], scale=[1.5, 0.8, 0.4])
        add_modifier(proj, "bevel", 3, params={"width": 0.02, "segments": 2})

        # Materials
        create_material(proj, name="White Wall", color=[0.95, 0.95, 0.95, 1])
        create_material(proj, name="Wood", color=[0.45, 0.3, 0.15, 1], roughness=0.7)
        assign_material(proj, 1, 1)
        assign_material(proj, 1, 2)
        assign_material(proj, 2, 3)

        # Lighting
        add_light(proj, light_type="AREA", name="WindowLight",
                  location=[10, 5, 2.5], rotation=[0, -90, 0], power=2000)

        # Camera
        add_camera(proj, name="Interior", location=[5, -5, 1.7],
                   rotation=[90, 0, 45], focal_length=24, set_active=True)

        path = os.path.join(tmp_dir, "arch.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        assert len(loaded["objects"]) == 4
        assert len(loaded["materials"]) == 3
