# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestComponentPresets:
    """Tests for expanded COMPONENT_PRESETS."""

    def test_preset_count(self):
        """Verify we have 29 component presets."""
        assert len(COMPONENT_PRESETS) == 29

    def test_all_presets_have_type(self):
        """Every preset must have a __type key."""
        for name, preset in COMPONENT_PRESETS.items():
            assert "__type" in preset, f"Preset '{name}' missing __type"
            assert preset["__type"].startswith("Sandbox."), (
                f"Preset '{name}' __type should start with Sandbox."
            )


class TestSceneModify:
    """Tests for modify_object and set_scene_properties."""

    def test_modify_object_name_and_position(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "OldName", position="0,0,0")

        result = modify_object(
            scene_path, guid=guid, new_name="NewName", position="100,200,300"
        )
        assert result["name"] == "NewName"
        assert "Name" in result["modified_fields"]
        assert "Position" in result["modified_fields"]

        objects = list_objects(scene_path)
        obj = [o for o in objects if o["guid"] == guid][0]
        assert obj["name"] == "NewName"
        assert obj["position"] == "100,200,300"

    def test_modify_object_selective(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "MyObj", position="10,20,30", scale="2,2,2")

        # Only modify position, scale should stay unchanged
        modify_object(scene_path, guid=guid, position="99,99,99")

        data = load_scene(scene_path)
        obj = find_object(data, guid=guid)
        assert obj["Position"] == "99,99,99"
        assert obj["Scale"] == "2,2,2"
        assert obj["Name"] == "MyObj"

    def test_modify_object_not_found(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)

        with pytest.raises(ValueError, match="not found"):
            modify_object(scene_path, guid="nonexistent-guid", new_name="X")

    def test_set_scene_properties(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, fixed_update_freq=50)

        props = set_scene_properties(scene_path, fixed_update_freq=64, timescale=0.5)
        assert props["FixedUpdateFrequency"] == 64
        assert props["TimeScale"] == 0.5

        # Verify persistence
        data = load_scene(scene_path)
        assert data["SceneProperties"]["FixedUpdateFrequency"] == 64
        assert data["SceneProperties"]["TimeScale"] == 0.5
