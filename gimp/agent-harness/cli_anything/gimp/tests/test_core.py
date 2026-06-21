# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_create_default(self):
        proj = create_project()
        assert proj["canvas"]["width"] == 1920
        assert proj["canvas"]["height"] == 1080
        assert proj["canvas"]["color_mode"] == "RGB"
        assert proj["version"] == "1.0"

    def test_create_with_dimensions(self):
        proj = create_project(width=800, height=600, dpi=150)
        assert proj["canvas"]["width"] == 800
        assert proj["canvas"]["height"] == 600
        assert proj["canvas"]["dpi"] == 150

    def test_create_with_profile(self):
        proj = create_project(profile="hd720p")
        assert proj["canvas"]["width"] == 1280
        assert proj["canvas"]["height"] == 720

    def test_create_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid color mode"):
            create_project(color_mode="XYZ")

    def test_create_invalid_dimensions(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_project(width=0, height=100)

    def test_save_and_open(self):
        proj = create_project(name="test_project")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            assert loaded["name"] == "test_project"
            assert loaded["canvas"]["width"] == 1920
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_project("/nonexistent/path.json")

    def test_get_info(self):
        proj = create_project(name="info_test")
        info = get_project_info(proj)
        assert info["name"] == "info_test"
        assert info["layer_count"] == 0
        assert "canvas" in info

    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) > 0
        names = [p["name"] for p in profiles]
        assert "hd1080p" in names
        assert "4k" in names
