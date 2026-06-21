# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSceneCloneAndGet:
    """Tests for clone_object, get_object, and set_navmesh_properties."""

    def test_clone_object(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(
            scene_path,
            "Original",
            position="10,20,30",
            components=["model", "rigidbody"],
        )

        result = clone_object(
            scene_path, guid=guid, new_name="Copy", position="100,0,0"
        )
        assert result["name"] == "Copy"
        assert result["original_name"] == "Original"
        assert result["guid"] != result["original_guid"]

        objects = list_objects(scene_path)
        names = [o["name"] for o in objects]
        assert "Original" in names
        assert "Copy" in names
        assert len(objects) == 2

    def test_clone_object_default_name(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        add_object(scene_path, "Box", position="0,0,0")

        result = clone_object(scene_path, name="Box")
        assert result["name"] == "Box (Clone)"

    def test_clone_object_new_guids(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "Obj", components=["model", "box_collider"])

        clone_result = clone_object(scene_path, guid=guid)
        data = load_scene(scene_path)

        # Collect all GUIDs - none should be duplicated
        all_guids = set()
        for obj in data["GameObjects"]:
            all_guids.add(obj["__guid"])
            for comp in obj.get("Components", []):
                guid_val = comp.get("__guid", "")
                assert guid_val not in all_guids or guid_val == "", (
                    f"Duplicate GUID: {guid_val}"
                )
                all_guids.add(guid_val)

    def test_get_object(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(
            scene_path, "TestObj", position="1,2,3", components=["model", "rigidbody"]
        )

        result = get_object(scene_path, guid=guid)
        assert result["name"] == "TestObj"
        assert result["guid"] == guid
        assert result["position"] == "1,2,3"
        assert len(result["components"]) == 2
        types = [c["type"] for c in result["components"]]
        assert "Sandbox.ModelRenderer" in types
        assert "Sandbox.Rigidbody" in types

    def test_get_object_not_found(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)

        with pytest.raises(ValueError, match="not found"):
            get_object(scene_path, guid="nonexistent")

    def test_set_navmesh_properties(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path)

        result = set_navmesh_properties(
            scene_path,
            navmesh_enabled=True,
            navmesh_agent_height=72,
            navmesh_agent_radius=16,
        )
        assert result["Enabled"] is True
        assert result["AgentHeight"] == 72
        assert result["AgentRadius"] == 16

        data = load_scene(scene_path)
        assert data["SceneProperties"]["NavMesh"]["Enabled"] is True
