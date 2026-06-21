# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAudioUtils:
    def test_generate_sine_wave(self):
        samples = generate_sine_wave(440, 0.1, 44100, 0.5, 1)
        assert len(samples) == 4410
        # Peak should be near 0.5
        assert max(abs(s) for s in samples) <= 0.51

    def test_generate_silence(self):
        samples = generate_silence(0.5, 44100, 1)
        assert len(samples) == 22050
        assert all(s == 0.0 for s in samples)

    def test_apply_gain(self):
        samples = [0.5, -0.5, 0.25]
        gained = apply_gain(samples, 6.0)
        # +6dB roughly doubles amplitude
        assert abs(gained[0] - 0.5 * 10 ** (6 / 20)) < 0.01

    def test_apply_fade_in(self):
        samples = [1.0] * 44100  # 1 second at 44100
        faded = apply_fade_in(samples, 0.5, 44100, 1)
        assert faded[0] == 0.0  # Start is silent
        assert abs(faded[-1] - 1.0) < 0.01  # End is unchanged

    def test_apply_fade_out(self):
        samples = [1.0] * 44100
        faded = apply_fade_out(samples, 0.5, 44100, 1)
        assert abs(faded[0] - 1.0) < 0.01  # Start unchanged
        assert abs(faded[-1]) < 0.01  # End is silent

    def test_apply_reverse(self):
        samples = [1.0, 2.0, 3.0, 4.0]
        reversed_s = apply_reverse(samples, 1)
        assert reversed_s == [4.0, 3.0, 2.0, 1.0]

    def test_apply_reverse_stereo(self):
        samples = [1.0, 2.0, 3.0, 4.0]  # 2 frames of stereo
        reversed_s = apply_reverse(samples, 2)
        assert reversed_s == [3.0, 4.0, 1.0, 2.0]

    def test_apply_echo(self):
        samples = [1.0] + [0.0] * 999
        echoed = apply_echo(
            samples, delay_ms=100, decay=0.5, sample_rate=1000, channels=1
        )
        # Echo at sample 100
        assert abs(echoed[100] - 0.5) < 0.01

    def test_apply_normalize(self):
        samples = [0.25, -0.25, 0.1]
        normalized = apply_normalize(samples, -1.0)
        peak = max(abs(s) for s in normalized)
        target = 10 ** (-1.0 / 20)
        assert abs(peak - target) < 0.01

    def test_apply_change_speed(self):
        samples = list(range(100))
        sped_up = apply_change_speed([float(s) for s in samples], 2.0, 1)
        assert len(sped_up) == 50

    def test_apply_limit(self):
        samples = [1.0, -1.0, 0.5, -0.5]
        limited = apply_limit(samples, -6.0)
        threshold = 10 ** (-6.0 / 20)
        for s in limited:
            assert abs(s) <= threshold + 0.001

    def test_clamp_samples(self):
        samples = [2.0, -2.0, 0.5]
        clamped = clamp_samples(samples)
        assert clamped == [1.0, -1.0, 0.5]

    def test_mix_audio(self):
        track1 = [0.5] * 10
        track2 = [0.3] * 10
        mixed = mix_audio([track1, track2], channels=1)
        assert abs(mixed[0] - 0.8) < 0.01

    def test_get_rms(self):
        samples = [0.5] * 100
        rms = get_rms(samples)
        assert abs(rms - 0.5) < 0.01

    def test_get_peak(self):
        samples = [0.3, -0.7, 0.5]
        assert get_peak(samples) == 0.7

    def test_db_from_linear(self):
        assert abs(db_from_linear(1.0)) < 0.01
        assert abs(db_from_linear(0.5) - (-6.02)) < 0.1


class TestExportPresets:
    def test_list_presets(self):
        presets = list_presets()
        assert len(presets) >= 4
        names = [p["name"] for p in presets]
        assert "wav" in names
        assert "mp3" in names

    def test_get_preset_info(self):
        info = get_preset_info("wav")
        assert info["format"] == "WAV"
        assert info["extension"] == ".wav"

    def test_get_preset_info_unknown(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset_info("nonexistent_format")

    def test_all_presets_valid(self):
        for name, preset in EXPORT_PRESETS.items():
            assert "format" in preset
            assert "ext" in preset
            assert "params" in preset
