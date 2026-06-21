# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProject:
    def test_create_default(self):
        proj = create_project()
        assert proj["settings"]["output_width"] == 1920
        assert proj["settings"]["output_height"] == 1080
        assert proj["settings"]["fps"] == 30
        assert proj["version"] == "1.0"
        assert len(proj["scenes"]) == 1

    def test_create_with_dimensions(self):
        proj = create_project(output_width=1280, output_height=720, fps=60)
        assert proj["settings"]["output_width"] == 1280
        assert proj["settings"]["output_height"] == 720
        assert proj["settings"]["fps"] == 60

    def test_create_with_encoder(self):
        proj = create_project(encoder="nvenc")
        assert proj["settings"]["encoder"] == "nvenc"

    def test_create_invalid_resolution(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_project(output_width=0)

    def test_create_invalid_fps(self):
        with pytest.raises(ValueError, match="must be positive"):
            create_project(fps=0)

    def test_create_invalid_encoder(self):
        with pytest.raises(ValueError, match="Invalid encoder"):
            create_project(encoder="bogus")

    def test_create_invalid_video_bitrate(self):
        with pytest.raises(ValueError, match="at least 100"):
            create_project(video_bitrate=10)

    def test_create_invalid_audio_bitrate(self):
        with pytest.raises(ValueError, match="at least 32"):
            create_project(audio_bitrate=8)

    def test_save_and_open(self):
        proj = create_project(name="test_proj")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)
            assert loaded["name"] == "test_proj"
            assert loaded["settings"]["output_width"] == 1920
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
            with pytest.raises(ValueError, match="Invalid"):
                open_project(path)
        finally:
            os.unlink(path)

    def test_get_info(self):
        proj = create_project(name="info_test")
        info = get_project_info(proj)
        assert info["name"] == "info_test"
        assert info["counts"]["scenes"] == 1
        assert "settings" in info

    def test_default_project_has_transitions(self):
        proj = create_project()
        assert len(proj["transitions"]) == 2

    def test_default_project_has_streaming(self):
        proj = create_project()
        assert proj["streaming"]["service"] == "twitch"

    def test_default_project_has_recording(self):
        proj = create_project()
        assert proj["recording"]["format"] == "mkv"

    def test_create_with_name(self):
        proj = create_project(name="my_stream")
        assert proj["name"] == "my_stream"
