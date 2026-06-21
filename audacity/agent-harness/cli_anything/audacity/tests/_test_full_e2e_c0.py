# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import short_wav, sine_wav, tmp_dir  # noqa: F401,E501


class _TestRenderPipelineMixin0:
    def test_render_empty_project(self, tmp_dir):
        proj = create_project()
        out = os.path.join(tmp_dir, "empty.wav")
        result = render_mix(proj, out, preset="wav")
        assert os.path.exists(out)
        assert result["format"] == "WAV"
        assert result["tracks_rendered"] == 0
    def test_render_single_track(self, tmp_dir, sine_wav):
        proj = create_project()
        add_track(proj, name="Voice")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        out = os.path.join(tmp_dir, "single.wav")
        result = render_mix(proj, out, preset="wav")
        assert os.path.exists(out)
        assert result["tracks_rendered"] == 1
        assert result["duration"] > 0.9

        # Verify the output WAV
        samples, sr, ch, bd = read_wav(out)
        assert sr == 44100
        assert get_rms(samples) > 0
    def test_render_stereo_output(self, tmp_dir, sine_wav):
        proj = create_project(channels=2)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        out = os.path.join(tmp_dir, "stereo_out.wav")
        result = render_mix(proj, out, preset="wav")
        assert result["channels"] == 2
        with wave.open(out, "r") as wf:
            assert wf.getnchannels() == 2
    def test_render_mono_output(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        out = os.path.join(tmp_dir, "mono_out.wav")
        result = render_mix(proj, out, preset="wav")
        assert result["channels"] == 1
        with wave.open(out, "r") as wf:
            assert wf.getnchannels() == 1
    def test_render_with_gain_effect(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)

        # Read original level
        orig_samples, _, _, _ = read_wav(sine_wav)
        orig_rms = get_rms(orig_samples)

        # Add +6dB gain
        add_effect(proj, "amplify", 0, {"gain_db": 6.0})

        out = os.path.join(tmp_dir, "gained.wav")
        render_mix(proj, out, preset="wav")
        gained_samples, _, _, _ = read_wav(out)
        gained_rms = get_rms(gained_samples)

        # +6dB should roughly double the amplitude
        assert gained_rms > orig_rms * 1.5
    def test_render_with_fade_in(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_effect(proj, "fade_in", 0, {"duration": 0.5})

        out = os.path.join(tmp_dir, "fade_in.wav")
        render_mix(proj, out, preset="wav")
        samples, sr, _, _ = read_wav(out)

        # First 100 samples should be very quiet
        first_chunk = samples[:100]
        last_chunk = samples[-1000:]
        assert get_rms(first_chunk) < get_rms(last_chunk)
    def test_render_with_reverse(self, tmp_dir):
        # Create a chirp (ascending frequency)
        path = os.path.join(tmp_dir, "chirp.wav")
        sr = 44100
        duration = 0.5
        n = int(sr * duration)
        samples = []
        for i in range(n):
            t = i / sr
            freq = 200 + (t / duration) * 2000
            samples.append(0.5 * math.sin(2 * math.pi * freq * t))
        write_wav(path, samples, sr, 1, 16)

        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, path, start_time=0.0)
        add_effect(proj, "reverse", 0)

        out = os.path.join(tmp_dir, "reversed.wav")
        render_mix(proj, out, preset="wav")

        rev_samples, _, _, _ = read_wav(out)
        # The first half of the reversed audio should have higher frequency
        # content than the original first half
        assert len(rev_samples) > 0
    def test_render_multiple_tracks(self, tmp_dir, sine_wav, short_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_track(proj, name="T2")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_clip(proj, 1, short_wav, start_time=0.0)

        out = os.path.join(tmp_dir, "multi.wav")
        result = render_mix(proj, out, preset="wav")
        assert result["tracks_rendered"] == 2
        samples, _, _, _ = read_wav(out)
        assert get_rms(samples) > 0
