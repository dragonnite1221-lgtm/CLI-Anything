# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestSceneLifecycle:
    def test_create_save_open_roundtrip(self, tmp_dir):
        proj = create_scene(name="roundtrip")
        path = os.path.join(tmp_dir, "scene.blend-cli.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        assert loaded["name"] == "roundtrip"
        assert loaded["render"]["resolution_x"] == 1920

    def test_scene_with_objects_roundtrip(self, tmp_dir):
        proj = create_scene(name="with_objects")
        add_object(proj, mesh_type="cube", name="MyCube")
        add_object(proj, mesh_type="sphere", name="MySphere")
        add_modifier(proj, "subdivision_surface", 0, params={"levels": 2})
        path = os.path.join(tmp_dir, "scene.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        assert len(loaded["objects"]) == 2
        assert loaded["objects"][0]["modifiers"][0]["type"] == "subdivision_surface"

    def test_scene_with_materials_roundtrip(self, tmp_dir):
        proj = create_scene(name="with_materials")
        create_material(proj, name="Red", color=[1, 0, 0, 1])
        add_object(proj, name="Cube")
        assign_material(proj, 0, 0)
        path = os.path.join(tmp_dir, "scene.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        assert len(loaded["materials"]) == 1
        assert loaded["objects"][0]["material"] == loaded["materials"][0]["id"]

    def test_scene_with_cameras_lights_roundtrip(self, tmp_dir):
        proj = create_scene(name="full_scene")
        add_camera(proj, name="MainCam", location=[7, -6, 5], rotation=[63, 0, 46])
        add_light(proj, light_type="SUN", name="Sun", rotation=[-30, 0, 0])
        add_light(proj, light_type="POINT", name="Fill", location=[3, 3, 3], power=500)
        path = os.path.join(tmp_dir, "scene.json")
        save_scene(proj, path)
        loaded = open_scene(path)
        assert len(loaded["cameras"]) == 1
        assert len(loaded["lights"]) == 2
        assert loaded["cameras"][0]["name"] == "MainCam"

    def test_scene_info_complete(self):
        proj = create_scene(name="info_test")
        add_object(proj, mesh_type="cube")
        add_object(proj, mesh_type="sphere")
        create_material(proj, name="Metal")
        add_camera(proj)
        add_light(proj)
        info = get_scene_info(proj)
        assert info["counts"]["objects"] == 2
        assert info["counts"]["materials"] == 1
        assert info["counts"]["cameras"] == 1
        assert info["counts"]["lights"] == 1

    def test_complex_scene_roundtrip(self, tmp_dir):
        """Create a complex scene, save, reload, verify integrity."""
        proj = create_scene(name="complex", engine="CYCLES", samples=256)

        # Add objects
        add_object(proj, mesh_type="plane", name="Ground", scale=[10, 10, 1])
        add_object(proj, mesh_type="cube", name="Box", location=[0, 0, 1])
        add_object(proj, mesh_type="sphere", name="Ball", location=[3, 0, 1.5])
        add_object(proj, mesh_type="monkey", name="Suzanne", location=[-3, 0, 1.5])

        # Add modifiers
        add_modifier(proj, "subdivision_surface", 1, params={"levels": 2})
        add_modifier(proj, "bevel", 1, params={"width": 0.1, "segments": 2})
        add_modifier(proj, "subdivision_surface", 2, params={"levels": 3})

        # Add materials
        create_material(proj, name="Ground", color=[0.3, 0.3, 0.3, 1], roughness=0.9)
        create_material(proj, name="Red Plastic", color=[0.8, 0.1, 0.1, 1], roughness=0.3)
        create_material(proj, name="Chrome", color=[0.9, 0.9, 0.9, 1], metallic=1.0, roughness=0.05)
        create_material(proj, name="Gold", color=[1.0, 0.8, 0.2, 1], metallic=1.0, roughness=0.2)

        # Assign materials
        assign_material(proj, 0, 0)  # Ground -> Ground mat
        assign_material(proj, 1, 1)  # Box -> Red Plastic
        assign_material(proj, 2, 2)  # Ball -> Chrome
        assign_material(proj, 3, 3)  # Suzanne -> Gold

        # Camera and lights
        add_camera(proj, name="Main", location=[7, -6, 5], rotation=[63, 0, 46], focal_length=50)
        add_light(proj, light_type="SUN", name="KeyLight", rotation=[-45, 0, 30])
        add_light(proj, light_type="AREA", name="FillLight", location=[4, 4, 3], power=500)

        # Animation
        add_keyframe(proj, 3, 1, "location", [-3, 0, 1.5])
        add_keyframe(proj, 3, 120, "location", [-3, 0, 3.0])
        add_keyframe(proj, 3, 1, "rotation", [0, 0, 0])
        add_keyframe(proj, 3, 120, "rotation", [0, 0, 360])

        # Frame range
        set_frame_range(proj, 1, 120)
        set_fps(proj, 30)

        # Save and reload
        path = os.path.join(tmp_dir, "complex.json")
        save_scene(proj, path)
        loaded = open_scene(path)

        assert len(loaded["objects"]) == 4
        assert len(loaded["materials"]) == 4
        assert len(loaded["cameras"]) == 1
        assert len(loaded["lights"]) == 2
        assert loaded["objects"][1]["modifiers"][0]["type"] == "subdivision_surface"
        assert loaded["objects"][1]["modifiers"][1]["type"] == "bevel"
        assert loaded["scene"]["fps"] == 30
        assert loaded["scene"]["frame_end"] == 120

        # Verify keyframes survived roundtrip
        suzanne = loaded["objects"][3]
        assert len(suzanne["keyframes"]) == 4
