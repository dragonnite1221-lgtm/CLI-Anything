# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_create_default(self):
        proj = create_project()
        assert proj["version"] == PROJECT_VERSION
        assert proj["profile"]["width"] == 1920
        assert proj["profile"]["height"] == 1080
        assert proj["profile"]["fps_num"] == 30
        assert proj["profile"]["fps_den"] == 1

    def test_create_with_name(self):
        proj = create_project(name="MyVideo")
        assert proj["name"] == "MyVideo"

    def test_create_with_profile(self):
        proj = create_project(profile="hd720p30")
        assert proj["profile"]["width"] == 1280
        assert proj["profile"]["height"] == 720
        assert proj["profile"]["fps_num"] == 30

    def test_create_4k_profile(self):
        proj = create_project(profile="4k30")
        assert proj["profile"]["width"] == 3840
        assert proj["profile"]["height"] == 2160

    def test_create_sd_pal_profile(self):
        proj = create_project(profile="sd_pal")
        assert proj["profile"]["width"] == 720
        assert proj["profile"]["height"] == 576
        assert proj["profile"]["progressive"] is False

    def test_create_invalid_profile(self):
        with pytest.raises(ValueError, match="Unknown profile"):
            create_project(profile="nonexistent")

    def test_create_invalid_resolution(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_project(width=0, height=100)

    def test_create_invalid_fps(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_project(fps_num=0)

    def test_create_custom_dimensions(self):
        proj = create_project(width=800, height=600, fps_num=25, fps_den=1)
        assert proj["profile"]["width"] == 800
        assert proj["profile"]["height"] == 600
        assert proj["profile"]["fps_num"] == 25

    def test_create_has_empty_collections(self):
        proj = create_project()
        assert proj["bin"] == []
        assert proj["tracks"] == []
        assert proj["transitions"] == []
        assert proj["guides"] == []

    def test_create_has_metadata(self):
        proj = create_project()
        assert "created" in proj["metadata"]
        assert "software" in proj["metadata"]

    def test_save_and_open(self):
        proj = create_project(name="test_proj")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            assert loaded["name"] == "test_proj"
            assert loaded["profile"]["width"] == 1920
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_project("/nonexistent/path.json")

    def test_open_invalid_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"invalid": True}, f)
            path = f.name
        try:
            with pytest.raises(ValueError, match="Invalid project file"):
                open_project(path)
        finally:
            os.unlink(path)

    def test_get_project_info(self):
        proj = create_project(name="info_test")
        info = get_project_info(proj)
        assert info["name"] == "info_test"
        assert info["counts"]["bin_clips"] == 0
        assert "profile" in info

    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) == len(PROFILES)
        names = [p["name"] for p in profiles]
        assert "hd1080p30" in names
        assert "4k30" in names
        assert "sd_pal" in names

    def test_all_profiles_valid(self):
        for name in PROFILES:
            proj = create_project(profile=name)
            assert proj["profile"]["width"] > 0
            assert proj["profile"]["height"] > 0
