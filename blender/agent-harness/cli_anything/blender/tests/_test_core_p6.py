# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestRender:
    def _make_scene(self):
        return create_scene()

    def test_set_render_settings_engine(self):
        proj = self._make_scene()
        result = set_render_settings(proj, engine="EEVEE")
        assert proj["render"]["engine"] == "EEVEE"

    def test_set_render_settings_resolution(self):
        proj = self._make_scene()
        set_render_settings(proj, resolution_x=3840, resolution_y=2160)
        assert proj["render"]["resolution_x"] == 3840
        assert proj["render"]["resolution_y"] == 2160

    def test_set_render_settings_samples(self):
        proj = self._make_scene()
        set_render_settings(proj, samples=512)
        assert proj["render"]["samples"] == 512

    def test_set_render_settings_invalid_engine(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Invalid engine"):
            set_render_settings(proj, engine="INVALID")

    def test_set_render_settings_invalid_resolution(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="must be positive"):
            set_render_settings(proj, resolution_x=0)

    def test_set_render_settings_with_preset(self):
        proj = self._make_scene()
        result = set_render_settings(proj, preset="cycles_high")
        assert proj["render"]["samples"] == 512

    def test_set_render_settings_invalid_preset(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Unknown render preset"):
            set_render_settings(proj, preset="nonexistent")

    def test_get_render_settings(self):
        proj = self._make_scene()
        info = get_render_settings(proj)
        assert info["engine"] == "CYCLES"
        assert "resolution" in info
        assert "effective_resolution" in info

    def test_list_render_presets(self):
        presets = list_render_presets()
        assert len(presets) >= 5
        names = [p["name"] for p in presets]
        assert "cycles_default" in names
        assert "eevee_default" in names

    def test_render_scene_generates_script(self):
        proj = self._make_scene()
        add_object(proj, name="Cube")
        with tempfile.TemporaryDirectory() as tmp:
            output_path = os.path.join(tmp, "render.png")
            result = render_scene(proj, output_path, overwrite=True)
            assert os.path.exists(result["script_path"])
            assert "blender" in result["command"]
            assert result["engine"] == "CYCLES"

    def test_render_scene_overwrite_protection(self):
        proj = self._make_scene()
        with tempfile.TemporaryDirectory() as tmp:
            output_path = os.path.join(tmp, "render.png")
            # Create the file first
            with open(output_path, "w") as f:
                f.write("existing")
            with pytest.raises(FileExistsError):
                render_scene(proj, output_path, overwrite=False)

    def test_all_engines_valid(self):
        assert "CYCLES" in VALID_ENGINES
        assert "EEVEE" in VALID_ENGINES
        assert "WORKBENCH" in VALID_ENGINES

    def test_render_settings_denoising(self):
        proj = self._make_scene()
        set_render_settings(proj, use_denoising=False)
        assert proj["render"]["use_denoising"] is False

    def test_render_settings_transparent(self):
        proj = self._make_scene()
        set_render_settings(proj, film_transparent=True)
        assert proj["render"]["film_transparent"] is True

    def test_render_settings_format(self):
        proj = self._make_scene()
        set_render_settings(proj, output_format="JPEG")
        assert proj["render"]["output_format"] == "JPEG"

    def test_render_settings_invalid_format(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Invalid format"):
            set_render_settings(proj, output_format="INVALID")
