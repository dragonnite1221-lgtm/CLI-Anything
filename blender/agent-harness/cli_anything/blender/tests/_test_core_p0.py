# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestScene:
    def test_create_default(self):
        proj = create_scene()
        assert proj["render"]["resolution_x"] == 1920
        assert proj["render"]["resolution_y"] == 1080
        assert proj["render"]["engine"] == "CYCLES"
        assert proj["version"] == "1.0"
        assert proj["scene"]["fps"] == 24

    def test_create_with_dimensions(self):
        proj = create_scene(resolution_x=800, resolution_y=600, samples=64)
        assert proj["render"]["resolution_x"] == 800
        assert proj["render"]["resolution_y"] == 600
        assert proj["render"]["samples"] == 64

    def test_create_with_profile(self):
        proj = create_scene(profile="hd720p")
        assert proj["render"]["resolution_x"] == 1280
        assert proj["render"]["resolution_y"] == 720

    def test_create_with_4k_profile(self):
        proj = create_scene(profile="4k")
        assert proj["render"]["resolution_x"] == 3840
        assert proj["render"]["resolution_y"] == 2160

    def test_create_invalid_engine(self):
        with pytest.raises(ValueError, match="Invalid render engine"):
            create_scene(engine="INVALID")

    def test_create_invalid_resolution(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_scene(resolution_x=0, resolution_y=100)

    def test_create_invalid_samples(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_scene(samples=0)

    def test_create_invalid_fps(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_scene(fps=0)

    def test_create_invalid_frame_range(self):
        with pytest.raises(ValueError, match="must be >= frame start"):
            create_scene(frame_start=100, frame_end=50)

    def test_save_and_open(self):
        proj = create_scene(name="test_scene")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_scene(proj, path)
            loaded = open_scene(path)
            assert loaded["name"] == "test_scene"
            assert loaded["render"]["resolution_x"] == 1920
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_scene("/nonexistent/path.json")

    def test_get_info(self):
        proj = create_scene(name="info_test")
        info = get_scene_info(proj)
        assert info["name"] == "info_test"
        assert info["counts"]["objects"] == 0
        assert "render" in info

    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) > 0
        names = [p["name"] for p in profiles]
        assert "hd1080p" in names
        assert "4k" in names
        assert "default" in names

    def test_scene_has_collections(self):
        proj = create_scene()
        assert len(proj["collections"]) == 1
        assert proj["collections"][0]["name"] == "Collection"

    def test_scene_has_world(self):
        proj = create_scene()
        assert "world" in proj
        assert "background_color" in proj["world"]

    def test_eevee_engine(self):
        proj = create_scene(engine="EEVEE")
        assert proj["render"]["engine"] == "EEVEE"
