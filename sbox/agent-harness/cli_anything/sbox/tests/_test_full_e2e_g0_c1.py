# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin1:
    def test_scene_manipulation_workflow(self, tmp_path):
        """Create project, add objects, remove objects, verify scene integrity."""
        from cli_anything.sbox.core import project as project_mod
        from cli_anything.sbox.core import scene as scene_mod

        # Create project
        project_mod.create_project(name="scene_test", output_dir=str(tmp_path))
        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")

        # Count initial objects
        initial_objects = scene_mod.list_objects(scene_path)
        initial_count = len(initial_objects)
        assert initial_count > 0, "Default scene should have objects"

        # Add 3 objects with different components
        guid1 = scene_mod.add_object(
            scene_path, "Cube",
            position="100,0,0",
            components=["model", "box_collider"],
        )
        guid2 = scene_mod.add_object(
            scene_path, "Sphere",
            position="0,100,0",
            components=["model", "sphere_collider", "rigidbody"],
        )
        guid3 = scene_mod.add_object(
            scene_path, "EmptyMarker",
            position="0,0,100",
        )

        assert guid1 and guid2 and guid3
        assert guid1 != guid2 != guid3

        # List objects - verify count increased by 3
        objects_after_add = scene_mod.list_objects(scene_path)
        assert len(objects_after_add) == initial_count + 3

        names = [o["name"] for o in objects_after_add]
        assert "Cube" in names
        assert "Sphere" in names
        assert "EmptyMarker" in names

        # Remove one object
        removed = scene_mod.remove_object(scene_path, name="Sphere")
        assert removed is True

        # List again - verify count decreased
        objects_after_remove = scene_mod.list_objects(scene_path)
        assert len(objects_after_remove) == initial_count + 2
        names_after = [o["name"] for o in objects_after_remove]
        assert "Sphere" not in names_after
        assert "Cube" in names_after
        assert "EmptyMarker" in names_after

        # Add component to existing object
        comp_guid = scene_mod.add_component(
            scene_path, guid1, "rigidbody",
        )
        assert comp_guid

        # Verify final scene is valid JSON with expected structure
        with open(scene_path, "r", encoding="utf-8") as f:
            final_scene = json.load(f)
        assert "GameObjects" in final_scene
        assert "SceneProperties" in final_scene
        assert "__version" in final_scene

        print(f"\n  Scene: {scene_path}")
        print(f"  Objects added: Cube({guid1}), Sphere({guid2}), EmptyMarker({guid3})")
        print(f"  Sphere removed, Cube got rigidbody({comp_guid})")
        print(f"  Final object count: {len(objects_after_remove)}")
