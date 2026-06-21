# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestLighting:
    def _make_scene(self):
        return create_scene()

    # Camera tests
    def test_add_camera(self):
        proj = self._make_scene()
        cam = add_camera(proj, name="Main Camera")
        assert cam["name"] == "Main Camera"
        assert cam["type"] == "PERSP"
        assert len(proj["cameras"]) == 1

    def test_add_camera_auto_active(self):
        proj = self._make_scene()
        cam = add_camera(proj)
        assert cam["is_active"] is True

    def test_add_camera_with_position(self):
        proj = self._make_scene()
        cam = add_camera(proj, location=[5, -5, 3], rotation=[60, 0, 45])
        assert cam["location"] == [5, -5, 3]
        assert cam["rotation"] == [60, 0, 45]

    def test_add_camera_invalid_type(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Invalid camera type"):
            add_camera(proj, camera_type="INVALID")

    def test_add_camera_invalid_focal_length(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Focal length must be positive"):
            add_camera(proj, focal_length=-1)

    def test_set_camera_property(self):
        proj = self._make_scene()
        add_camera(proj)
        set_camera(proj, 0, "focal_length", 85)
        assert proj["cameras"][0]["focal_length"] == 85.0

    def test_set_camera_location(self):
        proj = self._make_scene()
        add_camera(proj)
        set_camera(proj, 0, "location", [1.0, 2.0, 3.0])
        assert proj["cameras"][0]["location"] == [1.0, 2.0, 3.0]

    def test_set_camera_invalid_prop(self):
        proj = self._make_scene()
        add_camera(proj)
        with pytest.raises(ValueError, match="Unknown camera property"):
            set_camera(proj, 0, "bogus", 1)

    def test_set_active_camera(self):
        proj = self._make_scene()
        add_camera(proj, name="Cam1")
        add_camera(proj, name="Cam2")
        result = set_active_camera(proj, 1)
        assert result["active_camera"] == "Cam2"
        assert proj["cameras"][0]["is_active"] is False
        assert proj["cameras"][1]["is_active"] is True

    def test_list_cameras(self):
        proj = self._make_scene()
        add_camera(proj, name="A")
        add_camera(proj, name="B")
        result = list_cameras(proj)
        assert len(result) == 2

    def test_get_camera(self):
        proj = self._make_scene()
        add_camera(proj, name="Test")
        cam = get_camera(proj, 0)
        assert cam["name"] == "Test"

    # Light tests
    def test_add_point_light(self):
        proj = self._make_scene()
        light = add_light(proj, light_type="POINT")
        assert light["type"] == "POINT"
        assert "radius" in light
        assert len(proj["lights"]) == 1

    def test_add_sun_light(self):
        proj = self._make_scene()
        light = add_light(proj, light_type="SUN")
        assert light["type"] == "SUN"
        assert "angle" in light

    def test_add_spot_light(self):
        proj = self._make_scene()
        light = add_light(proj, light_type="SPOT")
        assert light["type"] == "SPOT"
        assert "spot_size" in light
        assert "spot_blend" in light

    def test_add_area_light(self):
        proj = self._make_scene()
        light = add_light(proj, light_type="AREA")
        assert light["type"] == "AREA"
        assert "size" in light
        assert "shape" in light

    def test_add_light_with_properties(self):
        proj = self._make_scene()
        light = add_light(proj, light_type="POINT", location=[1, 2, 3],
                          color=[1.0, 0.5, 0.0], power=500)
        assert light["location"] == [1, 2, 3]
        assert light["color"] == [1.0, 0.5, 0.0]
        assert light["power"] == 500

    def test_add_light_invalid_type(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Invalid light type"):
            add_light(proj, light_type="INVALID")

    def test_add_light_invalid_color(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="must be 0.0-1.0"):
            add_light(proj, color=[2.0, 0.0, 0.0])

    def test_set_light_property(self):
        proj = self._make_scene()
        add_light(proj)
        set_light(proj, 0, "power", 2000)
        assert proj["lights"][0]["power"] == 2000.0

    def test_set_light_color(self):
        proj = self._make_scene()
        add_light(proj)
        set_light(proj, 0, "color", [0.5, 0.5, 1.0])
        assert proj["lights"][0]["color"] == [0.5, 0.5, 1.0]

    def test_set_light_invalid_prop(self):
        proj = self._make_scene()
        add_light(proj)
        with pytest.raises(ValueError, match="Unknown light property"):
            set_light(proj, 0, "bogus", 1)

    def test_list_lights(self):
        proj = self._make_scene()
        add_light(proj, light_type="POINT", name="A")
        add_light(proj, light_type="SUN", name="B")
        result = list_lights(proj)
        assert len(result) == 2

    def test_get_light(self):
        proj = self._make_scene()
        add_light(proj, name="Test")
        light = get_light(proj, 0)
        assert light["name"] == "Test"
