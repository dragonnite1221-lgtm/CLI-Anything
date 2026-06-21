# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSceneRefs:
    """Tests for scene.extract_asset_refs."""

    def test_refs_from_default_scene(self, tmp_path):
        scene_path = str(tmp_path / "default.scene")
        create_scene("default", output_path=scene_path, include_defaults=True)
        refs = extract_asset_refs(scene_path)

        # The default scene has a model, materials, a sky material, and a cubemap
        assert "models" in refs
        assert "materials" in refs
        assert "textures" in refs
        # Check specific known refs from the default scene
        assert any("models/dev/plane.vmdl" in r for r in refs["models"])
        assert any("materials/skybox" in r for r in refs["materials"])

    def test_refs_dedup_and_sort(self, tmp_path):
        scene_path = str(tmp_path / "dup.scene")
        create_scene("dup", output_path=scene_path, include_defaults=False)
        # Add two objects that share the same model
        add_object(scene_path, "A", components=["model"])
        add_object(scene_path, "B", components=["model"])
        refs = extract_asset_refs(scene_path)
        # The model "models/dev/box.vmdl" appears in both objects but should be deduped
        assert refs["models"].count("models/dev/box.vmdl") == 1

    def test_refs_empty_scene(self, tmp_path):
        scene_path = str(tmp_path / "empty.scene")
        create_scene("empty", output_path=scene_path, include_defaults=False)
        refs = extract_asset_refs(scene_path)
        assert refs == {}


class TestSceneBulkModify:
    """Tests for scene.bulk_modify_objects."""

    def test_bulk_modify_position(self, tmp_path):
        scene_path = str(tmp_path / "bulk.scene")
        create_scene("bulk", output_path=scene_path, include_defaults=False)
        add_object(scene_path, "T1", position="0,0,0", tags="tower")
        add_object(scene_path, "T2", position="0,0,0", tags="tower")
        add_object(scene_path, "E1", position="0,0,0", tags="enemy")

        result = bulk_modify_objects(
            scene_path, has_tag="tower", new_position="100,200,300"
        )
        assert result["modified_count"] == 2
        assert result["modified_fields"] == ["Position"]

        towers = query_objects(scene_path, has_tag="tower")
        for t in towers:
            assert t["position"] == "100,200,300"
        # Enemy untouched
        enemies = query_objects(scene_path, has_tag="enemy")
        assert enemies[0]["position"] == "0,0,0"

    def test_bulk_modify_multiple_fields(self, tmp_path):
        scene_path = str(tmp_path / "bulk2.scene")
        create_scene("bulk2", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "X", position="0,0,0", tags="a")

        result = bulk_modify_objects(
            scene_path,
            has_tag="a",
            new_scale="2,2,2",
            new_tags="modified",
            new_enabled=False,
        )
        assert result["modified_count"] == 1
        assert set(result["modified_fields"]) == {"Scale", "Tags", "Enabled"}

        obj = get_object(scene_path, guid=guid)
        assert obj["scale"] == "2,2,2"
        assert obj["tags"] == "modified"
        assert obj["enabled"] is False

    def test_bulk_modify_no_matches(self, tmp_path):
        scene_path = str(tmp_path / "none.scene")
        create_scene("none", output_path=scene_path, include_defaults=False)
        result = bulk_modify_objects(scene_path, has_tag="nope", new_position="0,0,0")
        assert result["modified_count"] == 0
        assert result["modified_guids"] == []

    def test_bulk_modify_requires_update(self, tmp_path):
        scene_path = str(tmp_path / "req.scene")
        create_scene("req", output_path=scene_path, include_defaults=False)
        with pytest.raises(ValueError, match="at least one modification"):
            bulk_modify_objects(scene_path, has_tag="x")
