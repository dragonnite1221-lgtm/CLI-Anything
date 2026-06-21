# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestAudioProcessing:
    def test_gain_positive(self, tmp_dir):
        samples = generate_sine_wave(440, 0.5, 44100, 0.3, 1)
        gained = apply_gain(samples, 6.0)
        # +6dB should roughly double
        assert get_peak(gained) > get_peak(samples) * 1.8

    def test_gain_negative(self):
        samples = generate_sine_wave(440, 0.5, 44100, 0.5, 1)
        gained = apply_gain(samples, -6.0)
        assert get_peak(gained) < get_peak(samples) * 0.6

    def test_normalize_to_target(self):
        samples = generate_sine_wave(440, 0.5, 44100, 0.3, 1)
        normalized = apply_normalize(samples, -1.0)
        target = 10 ** (-1.0 / 20)
        assert abs(get_peak(normalized) - target) < 0.01

    def test_fade_in_effect(self):
        samples = [0.5] * 44100
        faded = apply_fade_in(samples, 0.5, 44100, 1)
        # First sample should be ~0
        assert abs(faded[0]) < 0.01
        # Sample at 25% of fade should be ~0.25 * original
        quarter = int(44100 * 0.25)
        assert abs(faded[quarter] - 0.5 * 0.5) < 0.05
        # After fade, should be full
        assert abs(faded[-1] - 0.5) < 0.01

    def test_fade_out_effect(self):
        samples = [0.5] * 44100
        faded = apply_fade_out(samples, 0.5, 44100, 1)
        assert abs(faded[0] - 0.5) < 0.01
        assert abs(faded[-1]) < 0.01

    def test_reverse_correctness(self):
        samples = [0.1, 0.2, 0.3, 0.4, 0.5]
        reversed_s = apply_reverse(samples, 1)
        assert reversed_s == [0.5, 0.4, 0.3, 0.2, 0.1]

    def test_echo_adds_delayed_copy(self):
        sr = 1000
        samples = [1.0] + [0.0] * 999
        echoed = apply_echo(samples, delay_ms=100, decay=0.5, sample_rate=sr, channels=1)
        # Original impulse at 0
        assert abs(echoed[0] - 1.0) < 0.01
        # Echo at sample 100
        assert abs(echoed[100] - 0.5) < 0.01
        # After echo, should be silence
        assert abs(echoed[200]) < 0.01

    def test_low_pass_attenuates_high_freq(self):
        sr = 44100
        # Mix of 100Hz and 10000Hz
        low = generate_sine_wave(100, 0.5, sr, 0.5, 1)
        high = generate_sine_wave(10000, 0.5, sr, 0.5, 1)
        mixed = [l + h for l, h in zip(low, high)]

        filtered = apply_low_pass(mixed, cutoff=500.0, sample_rate=sr, channels=1)

        # Analyze: filtered should have less high-frequency content
        arr = np.array(filtered)
        fft = np.abs(np.fft.rfft(arr))
        freqs = np.fft.rfftfreq(len(arr), 1.0 / sr)

        # Energy around 100Hz should be preserved
        low_mask = (freqs > 50) & (freqs < 200)
        high_mask = (freqs > 5000) & (freqs < 15000)

        low_energy = np.sum(fft[low_mask] ** 2)
        high_energy = np.sum(fft[high_mask] ** 2)

        # Low-pass should reduce high frequency energy significantly
        assert low_energy > high_energy * 2

    def test_high_pass_attenuates_low_freq(self):
        sr = 44100
        low = generate_sine_wave(50, 0.5, sr, 0.5, 1)
        high = generate_sine_wave(5000, 0.5, sr, 0.5, 1)
        mixed = [l + h for l, h in zip(low, high)]

        filtered = apply_high_pass(mixed, cutoff=1000.0, sample_rate=sr, channels=1)

        arr = np.array(filtered)
        fft = np.abs(np.fft.rfft(arr))
        freqs = np.fft.rfftfreq(len(arr), 1.0 / sr)

        low_mask = (freqs > 20) & (freqs < 100)
        high_mask = (freqs > 3000) & (freqs < 8000)

        low_energy = np.sum(fft[low_mask] ** 2)
        high_energy = np.sum(fft[high_mask] ** 2)

        assert high_energy > low_energy * 2

    def test_change_speed_doubles(self):
        samples = generate_sine_wave(440, 1.0, 44100, 0.5, 1)
        sped = apply_change_speed(samples, 2.0, 1)
        # Should be roughly half the length
        assert abs(len(sped) - len(samples) / 2) < 10

    def test_limiter_clamps_peak(self):
        samples = generate_sine_wave(440, 0.5, 44100, 0.9, 1)
        limited = apply_limit(samples, -6.0)
        threshold = 10 ** (-6.0 / 20)
        assert get_peak(limited) <= threshold + 0.001

    def test_mix_two_tracks(self):
        t1 = generate_sine_wave(440, 0.5, 44100, 0.3, 1)
        t2 = generate_sine_wave(880, 0.5, 44100, 0.3, 1)
        mixed = mix_audio([t1, t2], channels=1)
        # Mixed should have higher RMS than either alone
        assert get_rms(mixed) > get_rms(t1)
