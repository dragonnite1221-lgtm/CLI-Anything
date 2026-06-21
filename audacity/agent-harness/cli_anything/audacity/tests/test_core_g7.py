# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMediaProbe:
    def test_probe_wav(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            # Create a real WAV file
            samples = generate_sine_wave(440, 0.5, 44100, 0.5, 1)
            write_wav(path, samples, 44100, 1, 16)
            info = probe_audio(path)
            assert info["format"] == "WAV"
            assert info["sample_rate"] == 44100
            assert info["channels"] == 1
            assert info["bit_depth"] == 16
            assert abs(info["duration"] - 0.5) < 0.01
        finally:
            os.unlink(path)

    def test_probe_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            probe_audio("/nonexistent/audio.wav")

    def test_check_media_all_present(self):
        proj = create_project()
        add_track(proj, name="T")
        # No real files — just testing the check logic
        result = check_media(proj)
        assert result["status"] == "ok"
        assert result["total"] == 0

    def test_check_media_missing(self):
        proj = create_project()
        add_track(proj, name="T")
        add_clip(proj, 0, "/fake/missing.wav", start_time=0, end_time=1)
        result = check_media(proj)
        assert result["status"] == "missing_files"
        assert result["missing"] == 1

    def test_get_duration(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            samples = generate_sine_wave(440, 2.0, 44100, 0.5, 1)
            write_wav(path, samples, 44100, 1, 16)
            dur = get_duration(path)
            assert abs(dur - 2.0) < 0.01
        finally:
            os.unlink(path)
