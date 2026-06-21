# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMaterialUpdate:
    """Test material update functionality."""

    def test_update_metalness(self, tmp_path):
        path = str(tmp_path / "test.vmat")
        create_material("test", metalness=0.0, output_path=path)
        result = update_material(path, metalness=0.8)
        assert result["properties"]["g_flMetalness"] == "0.8"

    def test_update_texture(self, tmp_path):
        path = str(tmp_path / "test.vmat")
        create_material("test", output_path=path)
        result = update_material(path, color_texture="textures/new_color.tga")
        assert result["properties"]["TextureColor"] == "textures/new_color.tga"


class TestSoundUpdate:
    """Test sound event update functionality."""

    def test_update_volume(self, tmp_path):
        path = str(tmp_path / "test.sound")
        create_sound_event("test", volume="1", output_path=path)
        result = update_sound_event(path, volume="0.5")
        assert result["volume"] == "0.5"

    def test_update_sounds_list(self, tmp_path):
        path = str(tmp_path / "test.sound")
        create_sound_event("test", sounds=["a.vsnd"], output_path=path)
        result = update_sound_event(path, sounds=["b.vsnd", "c.vsnd"])
        assert result["sounds"] == ["b.vsnd", "c.vsnd"]


class TestSceneModifyComponent:
    """Tests for modify_component."""

    def test_modify_component_by_type(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "Obj", components=["rigidbody"])

        result = modify_component(
            scene_path,
            guid,
            component_type="Sandbox.Rigidbody",
            properties={"Gravity": False, "LinearDamping": 5},
        )
        assert "Gravity" in result["updated_keys"]
        assert "LinearDamping" in result["updated_keys"]

        data = load_scene(scene_path)
        obj = find_object(data, guid=guid)
        rb = [c for c in obj["Components"] if c["__type"] == "Sandbox.Rigidbody"][0]
        assert rb["Gravity"] is False
        assert rb["LinearDamping"] == 5

    def test_modify_component_not_found(self, tmp_path):
        scene_path = str(tmp_path / "test.scene")
        create_scene("test", output_path=scene_path, include_defaults=False)
        guid = add_object(scene_path, "Obj")

        with pytest.raises(ValueError, match="not found"):
            modify_component(
                scene_path,
                guid,
                component_type="Sandbox.Rigidbody",
                properties={"Gravity": False},
            )
