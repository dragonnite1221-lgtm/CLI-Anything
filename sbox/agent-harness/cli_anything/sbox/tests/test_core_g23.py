# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSceneInstantiatePrefab:
    """Tests for scene.instantiate_prefab."""

    def test_instantiate_default_name(self, tmp_path):
        scene_path = str(tmp_path / "level.scene")
        prefab_path = str(tmp_path / "Bullet.prefab")
        create_scene("level", output_path=scene_path, include_defaults=False)
        create_prefab("Bullet", output_path=prefab_path, components=["model"])

        guid = instantiate_prefab(scene_path, prefab_path, position="50,0,0")
        obj = get_object(scene_path, guid=guid)
        assert obj["name"] == "Bullet"
        assert obj["position"] == "50,0,0"

    def test_instantiate_with_override_name(self, tmp_path):
        scene_path = str(tmp_path / "level.scene")
        prefab_path = str(tmp_path / "Tower.prefab")
        create_scene("level", output_path=scene_path, include_defaults=False)
        create_prefab("Tower", output_path=prefab_path, components=["model"])

        guid = instantiate_prefab(scene_path, prefab_path, name="Tower_Spawn1")
        obj = get_object(scene_path, guid=guid)
        assert obj["name"] == "Tower_Spawn1"

    def test_instantiate_writes_prefab_source(self, tmp_path):
        scene_path = str(tmp_path / "level.scene")
        prefab_path = str(tmp_path / "P.prefab")
        create_scene("level", output_path=scene_path, include_defaults=False)
        create_prefab("P", output_path=prefab_path, components=["model"])

        instantiate_prefab(scene_path, prefab_path)
        data = load_scene(scene_path)
        # PrefabSource should be present on the new GameObject
        new_obj = data["GameObjects"][0]
        assert "PrefabSource" in new_obj
        assert "P.prefab" in new_obj["PrefabSource"]

    def test_instantiate_into_parent(self, tmp_path):
        scene_path = str(tmp_path / "level.scene")
        prefab_path = str(tmp_path / "Child.prefab")
        create_scene("level", output_path=scene_path, include_defaults=False)
        create_prefab("Child", output_path=prefab_path, components=["model"])

        parent_guid = add_object(scene_path, "Parent")
        child_guid = instantiate_prefab(
            scene_path, prefab_path, parent_guid=parent_guid
        )

        data = load_scene(scene_path)
        parent_obj = next(o for o in data["GameObjects"] if o["__guid"] == parent_guid)
        assert any(c["__guid"] == child_guid for c in parent_obj.get("Children", []))

    def test_instantiate_invalid_parent(self, tmp_path):
        scene_path = str(tmp_path / "level.scene")
        prefab_path = str(tmp_path / "P.prefab")
        create_scene("level", output_path=scene_path, include_defaults=False)
        create_prefab("P", output_path=prefab_path, components=["model"])

        with pytest.raises(ValueError, match="Parent"):
            instantiate_prefab(scene_path, prefab_path, parent_guid="bogus-guid")
