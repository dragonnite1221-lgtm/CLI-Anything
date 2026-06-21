# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSceneDiff:
    """Tests for scene.diff_scenes."""

    def test_identical_scenes(self, tmp_path):
        a = str(tmp_path / "a.scene")
        b = str(tmp_path / "b.scene")
        create_scene("x", output_path=a, include_defaults=False)
        # Same scene contents -> identical (GUIDs differ but we compare by Name)
        create_scene("x", output_path=b, include_defaults=False)
        result = diff_scenes(a, b)
        assert result["identical"] is True
        assert result["added"] == []
        assert result["removed"] == []
        assert result["modified"] == []

    def test_added_and_removed(self, tmp_path):
        a = str(tmp_path / "a.scene")
        b = str(tmp_path / "b.scene")
        create_scene("x", output_path=a, include_defaults=False)
        create_scene("x", output_path=b, include_defaults=False)
        add_object(a, "OnlyInA")
        add_object(a, "Shared")
        add_object(b, "Shared")
        add_object(b, "OnlyInB")

        result = diff_scenes(a, b)
        assert result["added"] == ["OnlyInB"]
        assert result["removed"] == ["OnlyInA"]
        assert result["modified"] == []
        assert result["identical"] is False

    def test_modified_position(self, tmp_path):
        a = str(tmp_path / "a.scene")
        b = str(tmp_path / "b.scene")
        create_scene("x", output_path=a, include_defaults=False)
        create_scene("x", output_path=b, include_defaults=False)
        add_object(a, "Box", position="0,0,0")
        add_object(b, "Box", position="100,200,300")

        result = diff_scenes(a, b)
        assert len(result["modified"]) == 1
        m = result["modified"][0]
        assert m["name"] == "Box"
        assert "position" in m["changes"]
        assert m["changes"]["position"]["from"] == "0,0,0"
        assert m["changes"]["position"]["to"] == "100,200,300"

    def test_modified_components(self, tmp_path):
        a = str(tmp_path / "a.scene")
        b = str(tmp_path / "b.scene")
        create_scene("x", output_path=a, include_defaults=False)
        create_scene("x", output_path=b, include_defaults=False)
        add_object(a, "X", components=["model"])
        add_object(b, "X", components=["model", "rigidbody"])

        result = diff_scenes(a, b)
        assert len(result["modified"]) == 1
        m = result["modified"][0]
        assert "components_added" in m["changes"]
        assert "Sandbox.Rigidbody" in m["changes"]["components_added"]

    def test_scene_property_changes(self, tmp_path):
        a = str(tmp_path / "a.scene")
        b = str(tmp_path / "b.scene")
        create_scene("x", output_path=a, include_defaults=False)
        create_scene("x", output_path=b, include_defaults=False)
        set_scene_properties(b, fixed_update_freq=120)

        result = diff_scenes(a, b)
        assert "FixedUpdateFrequency" in result["scene_property_changes"]


class TestPrefabDiff:
    """Tests for prefab.diff_prefabs."""

    def test_identical_prefabs(self, tmp_path):
        a = str(tmp_path / "a.prefab")
        b = str(tmp_path / "b.prefab")
        create_prefab("P", output_path=a, components=["model", "rigidbody"])
        create_prefab("P", output_path=b, components=["model", "rigidbody"])
        result = diff_prefabs(a, b)
        assert result["identical"] is True

    def test_root_changes(self, tmp_path):
        a = str(tmp_path / "a.prefab")
        b = str(tmp_path / "b.prefab")
        create_prefab("P", output_path=a, components=["model"])
        create_prefab("P", output_path=b, components=["model", "rigidbody"])
        result = diff_prefabs(a, b)
        assert result["identical"] is False
        assert result["root_changes"] is not None
        assert "components_added" in result["root_changes"]["changes"]
