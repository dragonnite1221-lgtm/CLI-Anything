# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSceneQuery:
    """Tests for scene.query_objects."""

    def _make_test_scene(self, tmp_path):
        scene_path = str(tmp_path / "q.scene")
        create_scene("q", output_path=scene_path, include_defaults=False)
        add_object(
            scene_path,
            "Tower1",
            position="100,0,0",
            tags="tower,placed",
            components=["model", "rigidbody"],
        )
        add_object(
            scene_path, "Tower2", position="200,0,0", tags="tower", components=["model"]
        )
        add_object(
            scene_path,
            "Enemy1",
            position="0,500,0",
            tags="enemy",
            components=["skinned_model_renderer", "rigidbody"],
        )
        add_object(scene_path, "Disabled", position="0,0,0", tags="")
        # Disable the last one
        modify_object(scene_path, name_match="Disabled", enabled=False)
        return scene_path

    def test_query_by_component_preset(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, has_component="rigidbody")
        names = sorted(r["name"] for r in result)
        assert names == ["Enemy1", "Tower1"]

    def test_query_by_component_full_type(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, has_component="Sandbox.SkinnedModelRenderer")
        assert len(result) == 1
        assert result[0]["name"] == "Enemy1"

    def test_query_by_tag(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, has_tag="tower")
        names = sorted(r["name"] for r in result)
        assert names == ["Tower1", "Tower2"]

    def test_query_by_name_substring(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, name_match="Tower")
        assert len(result) == 2

    def test_query_by_name_regex(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, name_regex=r"^Tower\d$")
        assert len(result) == 2

    def test_query_by_bounds(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        # Bounds that capture only the Towers (x in [50, 250])
        result = query_objects(path, in_bounds="50,-1,-1,250,1,1")
        names = sorted(r["name"] for r in result)
        assert names == ["Tower1", "Tower2"]

    def test_query_by_enabled(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, enabled=False)
        assert len(result) == 1
        assert result[0]["name"] == "Disabled"

    def test_query_combined_filters_and(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        # tower tag AND has rigidbody = only Tower1
        result = query_objects(path, has_tag="tower", has_component="rigidbody")
        assert len(result) == 1
        assert result[0]["name"] == "Tower1"

    def test_query_no_matches(self, tmp_path):
        path = self._make_test_scene(tmp_path)
        result = query_objects(path, has_tag="nonexistent")
        assert result == []
