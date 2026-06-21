# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestScenes:
    def _make_project(self):
        return create_project()

    def test_add_scene(self):
        proj = self._make_project()
        scene = add_scene(proj, name="BRB")
        assert scene["name"] == "BRB"
        assert len(proj["scenes"]) == 2

    def test_add_scene_unique_name(self):
        proj = self._make_project()
        s1 = add_scene(proj, name="Game")
        s2 = add_scene(proj, name="Game")
        assert s1["name"] != s2["name"]

    def test_add_scene_unique_ids(self):
        proj = self._make_project()
        s1 = add_scene(proj, name="A")
        s2 = add_scene(proj, name="B")
        assert s1["id"] != s2["id"]

    def test_remove_scene(self):
        proj = self._make_project()
        add_scene(proj, name="Extra")
        removed = remove_scene(proj, 1)
        assert removed["name"] == "Extra"
        assert len(proj["scenes"]) == 1

    def test_remove_last_scene_fails(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Cannot remove the last scene"):
            remove_scene(proj, 0)

    def test_remove_scene_invalid_index(self):
        proj = self._make_project()
        with pytest.raises(IndexError):
            remove_scene(proj, 99)

    def test_duplicate_scene(self):
        proj = self._make_project()
        dup = duplicate_scene(proj, 0)
        assert "Copy" in dup["name"]
        assert len(proj["scenes"]) == 2
        assert dup["id"] != proj["scenes"][0]["id"]

    def test_set_active_scene(self):
        proj = self._make_project()
        add_scene(proj, name="BRB")
        result = set_active_scene(proj, 1)
        assert result["index"] == 1
        assert proj["active_scene"] == 1

    def test_set_active_scene_invalid(self):
        proj = self._make_project()
        with pytest.raises(IndexError):
            set_active_scene(proj, 99)

    def test_list_scenes(self):
        proj = self._make_project()
        add_scene(proj, name="BRB")
        result = list_scenes(proj)
        assert len(result) == 2
        assert result[0]["active"] is True
        assert result[1]["active"] is False

    def test_remove_scene_fixes_active(self):
        proj = self._make_project()
        add_scene(proj, name="A")
        add_scene(proj, name="B")
        proj["active_scene"] = 2
        remove_scene(proj, 2)
        assert proj["active_scene"] <= len(proj["scenes"]) - 1
