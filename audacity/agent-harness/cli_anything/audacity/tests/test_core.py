# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_create_default(self):
        proj = create_project()
        assert proj["settings"]["sample_rate"] == 44100
        assert proj["settings"]["bit_depth"] == 16
        assert proj["settings"]["channels"] == 2
        assert proj["version"] == "1.0"
        assert proj["name"] == "untitled"

    def test_create_with_name(self):
        proj = create_project(name="My Podcast")
        assert proj["name"] == "My Podcast"

    def test_create_with_custom_settings(self):
        proj = create_project(sample_rate=48000, bit_depth=24, channels=1)
        assert proj["settings"]["sample_rate"] == 48000
        assert proj["settings"]["bit_depth"] == 24
        assert proj["settings"]["channels"] == 1

    def test_create_invalid_sample_rate(self):
        with pytest.raises(ValueError, match="Invalid sample rate"):
            create_project(sample_rate=12345)

    def test_create_invalid_bit_depth(self):
        with pytest.raises(ValueError, match="Invalid bit depth"):
            create_project(bit_depth=20)

    def test_create_invalid_channels(self):
        with pytest.raises(ValueError, match="Invalid channel count"):
            create_project(channels=5)

    def test_save_and_open(self):
        proj = create_project(name="test_project")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            assert loaded["name"] == "test_project"
            assert loaded["settings"]["sample_rate"] == 44100
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            open_project("/nonexistent/path.json")

    def test_open_invalid(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"foo": "bar"}, f)
            path = f.name
        try:
            with pytest.raises(ValueError, match="Invalid project"):
                open_project(path)
        finally:
            os.unlink(path)

    def test_get_info(self):
        proj = create_project(name="info_test")
        info = get_project_info(proj)
        assert info["name"] == "info_test"
        assert info["track_count"] == 0
        assert info["clip_count"] == 0
        assert "settings" in info

    def test_set_settings(self):
        proj = create_project()
        result = set_settings(proj, sample_rate=48000)
        assert result["sample_rate"] == 48000
        assert proj["settings"]["sample_rate"] == 48000

    def test_set_settings_invalid(self):
        proj = create_project()
        with pytest.raises(ValueError):
            set_settings(proj, sample_rate=99999)
