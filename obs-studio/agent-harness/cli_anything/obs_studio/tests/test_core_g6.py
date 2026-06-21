# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestOutput:
    def _make_project(self):
        return create_project()

    def test_set_streaming(self):
        proj = self._make_project()
        result = set_streaming(proj, service="youtube")
        assert result["service"] == "youtube"

    def test_set_streaming_invalid_service(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid streaming service"):
            set_streaming(proj, service="bogus")

    def test_set_streaming_key(self):
        proj = self._make_project()
        result = set_streaming(proj, key="abc123")
        assert result["key"] == "abc123"

    def test_set_recording(self):
        proj = self._make_project()
        result = set_recording(proj, fmt="mp4", quality="lossless")
        assert result["format"] == "mp4"
        assert result["quality"] == "lossless"

    def test_set_recording_invalid_format(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid recording format"):
            set_recording(proj, fmt="avi")

    def test_set_recording_invalid_quality(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid recording quality"):
            set_recording(proj, quality="ultra")

    def test_set_output_settings(self):
        proj = self._make_project()
        result = set_output_settings(proj, output_width=1280, output_height=720)
        assert result["output_width"] == 1280

    def test_set_output_settings_with_preset(self):
        proj = self._make_project()
        result = set_output_settings(proj, preset="quality")
        assert result["video_bitrate"] == 8000

    def test_set_output_settings_invalid_preset(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Unknown encoding preset"):
            set_output_settings(proj, preset="nonexistent")

    def test_set_output_settings_invalid_width(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="must be positive"):
            set_output_settings(proj, output_width=0)

    def test_set_output_settings_invalid_encoder(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid encoder"):
            set_output_settings(proj, encoder="bogus")

    def test_get_output_info(self):
        proj = self._make_project()
        info = get_output_info(proj)
        assert "settings" in info
        assert "streaming" in info
        assert "recording" in info

    def test_list_encoding_presets(self):
        presets = list_encoding_presets()
        assert len(presets) == len(ENCODING_PRESETS)
        names = [p["name"] for p in presets]
        assert "balanced" in names

    def test_valid_services(self):
        assert "twitch" in VALID_SERVICES
        assert "youtube" in VALID_SERVICES

    def test_valid_formats(self):
        assert "mkv" in VALID_RECORDING_FORMATS
        assert "mp4" in VALID_RECORDING_FORMATS
