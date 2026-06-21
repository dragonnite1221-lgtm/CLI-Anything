# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import short_wav, sine_wav, stereo_wav, tmp_dir  # noqa: F401,E501


class _TestRenderPipelineMixin1:
    def test_render_muted_track_excluded(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_track(proj, name="T2 (muted)")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_clip(proj, 1, sine_wav, start_time=0.0)

        # Mute track 1
        set_track_property(proj, 1, "mute", "true")

        out = os.path.join(tmp_dir, "muted.wav")
        result = render_mix(proj, out, preset="wav")
        assert result["tracks_rendered"] == 1
    def test_render_solo_track(self, tmp_dir, sine_wav, short_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_track(proj, name="T2 (solo)")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_clip(proj, 1, short_wav, start_time=0.0)

        # Solo track 1 only
        set_track_property(proj, 1, "solo", "true")

        out = os.path.join(tmp_dir, "solo.wav")
        result = render_mix(proj, out, preset="wav")
        assert result["tracks_rendered"] == 1
    def test_render_overwrite_protection(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)

        out = os.path.join(tmp_dir, "existing.wav")
        render_mix(proj, out, preset="wav")
        with pytest.raises(FileExistsError):
            render_mix(proj, out, preset="wav")

        # With overwrite flag
        result = render_mix(proj, out, preset="wav", overwrite=True)
        assert os.path.exists(out)
    def test_render_with_echo(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_effect(proj, "echo", 0, {"delay_ms": 200, "decay": 0.5})

        out = os.path.join(tmp_dir, "echo.wav")
        result = render_mix(proj, out, preset="wav")

        # Echo should extend the duration
        samples, _, _, _ = read_wav(out)
        assert len(samples) / 44100 > 1.0  # Longer than original 1s
    def test_render_with_compression(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_effect(proj, "compress", 0, {"threshold": -10.0, "ratio": 4.0})

        out = os.path.join(tmp_dir, "compressed.wav")
        render_mix(proj, out, preset="wav")
        samples, _, _, _ = read_wav(out)
        assert len(samples) > 0
    def test_render_24bit(self, tmp_dir, sine_wav):
        proj = create_project(channels=1, bit_depth=24)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)

        out = os.path.join(tmp_dir, "out24.wav")
        result = render_mix(proj, out, preset="wav-24")
        assert result["bit_depth"] == 24
        with wave.open(out, "r") as wf:
            assert wf.getsampwidth() == 3
    def test_render_channel_override(self, tmp_dir, stereo_wav):
        proj = create_project(channels=2)
        add_track(proj, name="T1")
        add_clip(proj, 0, stereo_wav, start_time=0.0)

        out = os.path.join(tmp_dir, "mono_override.wav")
        result = render_mix(proj, out, preset="wav", channels_override=1)
        assert result["channels"] == 1
        with wave.open(out, "r") as wf:
            assert wf.getnchannels() == 1
