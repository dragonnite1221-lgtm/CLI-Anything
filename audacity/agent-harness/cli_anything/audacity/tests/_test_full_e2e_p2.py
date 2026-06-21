# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import short_wav, sine_wav, tmp_dir  # noqa: F401,E501


class TestProjectLifecycle:
    def test_full_workflow(self, tmp_dir, sine_wav, short_wav):
        """Full podcast-style workflow: create, add tracks, clips, effects, export."""
        proj = create_project(name="My Podcast", channels=1)

        # Add tracks
        add_track(proj, name="Host Voice")
        add_track(proj, name="Guest Voice")
        add_track(proj, name="Music Bed")

        # Add clips
        add_clip(proj, 0, sine_wav, start_time=0.0, name="Host Intro")
        add_clip(proj, 1, short_wav, start_time=0.5, name="Guest Reply")
        add_clip(proj, 2, sine_wav, start_time=0.0, name="Background Music",
                 volume=0.3)

        # Add effects
        add_effect(proj, "normalize", 0, {"target_db": -3.0})
        add_effect(proj, "fade_in", 2, {"duration": 0.5})
        add_effect(proj, "fade_out", 2, {"duration": 0.5})

        # Add labels
        add_label(proj, 0.0, text="Start")
        add_label(proj, 0.5, 1.0, text="Guest segment")

        # Save project
        proj_path = os.path.join(tmp_dir, "podcast.json")
        save_project(proj, proj_path)

        # Reload
        loaded = open_project(proj_path)
        info = get_project_info(loaded)
        assert info["track_count"] == 3
        assert info["clip_count"] == 3
        assert info["label_count"] == 2

        # Export
        out = os.path.join(tmp_dir, "podcast.wav")
        result = render_mix(loaded, out, preset="wav")
        assert os.path.exists(out)
        assert result["tracks_rendered"] == 3

        # Verify output
        samples, sr, ch, bd = read_wav(out)
        assert sr == 44100
        assert ch == 1
        assert get_rms(samples) > 0

    def test_save_open_roundtrip_preserves_effects(self, tmp_dir, sine_wav):
        proj = create_project(name="roundtrip")
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0)
        add_effect(proj, "amplify", 0, {"gain_db": 3.0})
        add_effect(proj, "echo", 0, {"delay_ms": 200, "decay": 0.3})

        path = os.path.join(tmp_dir, "roundtrip.json")
        save_project(proj, path)
        loaded = open_project(path)

        effects = list_effects(loaded, 0)
        assert len(effects) == 2
        assert effects[0]["name"] == "amplify"
        assert effects[0]["params"]["gain_db"] == 3.0
        assert effects[1]["name"] == "echo"

    def test_multiple_clips_timeline(self, tmp_dir, sine_wav, short_wav):
        """Test that clips are placed at correct positions on the timeline."""
        proj = create_project(channels=1)
        add_track(proj, name="T1")

        # Place clips at specific positions
        add_clip(proj, 0, sine_wav, start_time=0.0, name="Clip A")
        add_clip(proj, 0, short_wav, start_time=1.5, name="Clip B")

        out = os.path.join(tmp_dir, "timeline.wav")
        result = render_mix(proj, out, preset="wav")

        # Duration should cover both clips
        assert result["duration"] >= 1.9  # 1.5 + 0.5 = 2.0

    def test_clip_split_and_move(self, tmp_dir, sine_wav):
        proj = create_project(channels=1)
        add_track(proj, name="T1")
        add_clip(proj, 0, sine_wav, start_time=0.0, end_time=1.0,
                 trim_start=0.0, trim_end=1.0)

        # Split at 0.5
        parts = split_clip(proj, 0, 0, 0.5)
        assert len(parts) == 2

        # Move second part to 2.0
        move_clip(proj, 0, 1, 2.0)

        clips = list_clips(proj, 0)
        assert clips[0]["end_time"] == 0.5
        assert clips[1]["start_time"] == 2.0
