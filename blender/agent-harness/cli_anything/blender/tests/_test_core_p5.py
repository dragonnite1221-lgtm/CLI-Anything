# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestAnimation:
    def _make_scene_with_object(self):
        proj = create_scene()
        add_object(proj, name="Cube")
        return proj

    def test_add_keyframe_location(self):
        proj = self._make_scene_with_object()
        kf = add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        assert kf["frame"] == 1
        assert kf["property"] == "location"
        assert kf["value"] == [0.0, 0.0, 0.0]

    def test_add_keyframe_rotation(self):
        proj = self._make_scene_with_object()
        kf = add_keyframe(proj, 0, 10, "rotation", [0, 0, 90])
        assert kf["value"] == [0.0, 0.0, 90.0]

    def test_add_keyframe_scale(self):
        proj = self._make_scene_with_object()
        kf = add_keyframe(proj, 0, 10, "scale", [2, 2, 2])
        assert kf["value"] == [2.0, 2.0, 2.0]

    def test_add_keyframe_visible(self):
        proj = self._make_scene_with_object()
        kf = add_keyframe(proj, 0, 10, "visible", "true")
        assert kf["value"] is True

    def test_add_keyframe_invalid_property(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="Cannot animate"):
            add_keyframe(proj, 0, 1, "bogus", 1)

    def test_add_keyframe_invalid_interpolation(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="Invalid interpolation"):
            add_keyframe(proj, 0, 1, "location", [0, 0, 0], "INVALID")

    def test_add_keyframe_replaces_existing(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 1, "location", [1, 1, 1])
        assert len(proj["objects"][0]["keyframes"]) == 1
        assert proj["objects"][0]["keyframes"][0]["value"] == [1.0, 1.0, 1.0]

    def test_remove_keyframe(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        removed = remove_keyframe(proj, 0, 1)
        assert len(removed) == 1
        assert len(proj["objects"][0]["keyframes"]) == 0

    def test_remove_keyframe_by_property(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 1, "rotation", [0, 0, 0])
        removed = remove_keyframe(proj, 0, 1, "location")
        assert len(removed) == 1
        assert len(proj["objects"][0]["keyframes"]) == 1

    def test_remove_keyframe_not_found(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="No keyframe found"):
            remove_keyframe(proj, 0, 999)

    def test_set_frame_range(self):
        proj = self._make_scene_with_object()
        result = set_frame_range(proj, 1, 500)
        assert proj["scene"]["frame_start"] == 1
        assert proj["scene"]["frame_end"] == 500
        assert "old_range" in result

    def test_set_frame_range_invalid(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="must be >="):
            set_frame_range(proj, 100, 50)

    def test_set_fps(self):
        proj = self._make_scene_with_object()
        result = set_fps(proj, 30)
        assert proj["scene"]["fps"] == 30
        assert result["old_fps"] == 24

    def test_set_fps_invalid(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="must be positive"):
            set_fps(proj, 0)

    def test_set_current_frame(self):
        proj = self._make_scene_with_object()
        result = set_current_frame(proj, 100)
        assert proj["scene"]["frame_current"] == 100

    def test_set_current_frame_out_of_range(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="outside range"):
            set_current_frame(proj, 9999)

    def test_list_keyframes(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 10, "location", [5, 5, 5])
        add_keyframe(proj, 0, 10, "rotation", [0, 0, 90])
        result = list_keyframes(proj, 0)
        assert len(result) == 3

    def test_list_keyframes_filtered(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        add_keyframe(proj, 0, 10, "rotation", [0, 0, 90])
        result = list_keyframes(proj, 0, prop="location")
        assert len(result) == 1

    def test_keyframes_sorted(self):
        proj = self._make_scene_with_object()
        add_keyframe(proj, 0, 50, "location", [5, 5, 5])
        add_keyframe(proj, 0, 1, "location", [0, 0, 0])
        kfs = proj["objects"][0]["keyframes"]
        assert kfs[0]["frame"] <= kfs[1]["frame"]
