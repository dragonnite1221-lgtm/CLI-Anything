# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestClips:
    def _make_project_with_track(self):
        proj = create_project()
        add_track(proj, name="Track 1")
        return proj

    def test_add_clip(self):
        proj = self._make_project_with_track()
        clip = add_clip(
            proj, 0, "/fake/audio.wav", name="Test Clip", start_time=0.0, end_time=10.0
        )
        assert clip["name"] == "Test Clip"
        assert clip["start_time"] == 0.0
        assert clip["end_time"] == 10.0

    def test_add_clip_auto_name(self):
        proj = self._make_project_with_track()
        clip = add_clip(proj, 0, "/fake/recording.wav", start_time=0.0, end_time=5.0)
        assert clip["name"] == "recording"

    def test_add_clip_out_of_range(self):
        proj = self._make_project_with_track()
        with pytest.raises(IndexError):
            add_clip(proj, 5, "/fake/audio.wav", start_time=0.0, end_time=1.0)

    def test_add_clip_invalid_times(self):
        proj = self._make_project_with_track()
        with pytest.raises(ValueError):
            add_clip(proj, 0, "/fake/audio.wav", start_time=10.0, end_time=5.0)

    def test_remove_clip(self):
        proj = self._make_project_with_track()
        add_clip(
            proj, 0, "/fake/audio.wav", name="Remove Me", start_time=0.0, end_time=5.0
        )
        removed = remove_clip(proj, 0, 0)
        assert removed["name"] == "Remove Me"
        assert len(proj["tracks"][0]["clips"]) == 0

    def test_remove_clip_out_of_range(self):
        proj = self._make_project_with_track()
        with pytest.raises(IndexError):
            remove_clip(proj, 0, 0)

    def test_split_clip(self):
        proj = self._make_project_with_track()
        add_clip(
            proj,
            0,
            "/fake/audio.wav",
            name="Full",
            start_time=0.0,
            end_time=10.0,
            trim_start=0.0,
            trim_end=10.0,
        )
        parts = split_clip(proj, 0, 0, 5.0)
        assert len(parts) == 2
        assert parts[0]["end_time"] == 5.0
        assert parts[1]["start_time"] == 5.0
        assert len(proj["tracks"][0]["clips"]) == 2

    def test_split_clip_invalid_time(self):
        proj = self._make_project_with_track()
        add_clip(proj, 0, "/fake/audio.wav", start_time=0.0, end_time=10.0)
        with pytest.raises(ValueError, match="Split time"):
            split_clip(proj, 0, 0, 0.0)
        with pytest.raises(ValueError, match="Split time"):
            split_clip(proj, 0, 0, 15.0)

    def test_move_clip(self):
        proj = self._make_project_with_track()
        add_clip(proj, 0, "/fake/audio.wav", start_time=0.0, end_time=5.0)
        result = move_clip(proj, 0, 0, 10.0)
        assert result["start_time"] == 10.0
        assert result["end_time"] == 15.0

    def test_move_clip_negative(self):
        proj = self._make_project_with_track()
        add_clip(proj, 0, "/fake/audio.wav", start_time=5.0, end_time=10.0)
        with pytest.raises(ValueError):
            move_clip(proj, 0, 0, -1.0)

    def test_trim_clip(self):
        proj = self._make_project_with_track()
        add_clip(
            proj,
            0,
            "/fake/audio.wav",
            name="Trim",
            start_time=0.0,
            end_time=10.0,
            trim_start=0.0,
            trim_end=10.0,
        )
        result = trim_clip(proj, 0, 0, trim_end=8.0)
        assert result["trim_end"] == 8.0

    def test_list_clips(self):
        proj = self._make_project_with_track()
        add_clip(proj, 0, "/fake/a.wav", name="A", start_time=0.0, end_time=5.0)
        add_clip(proj, 0, "/fake/b.wav", name="B", start_time=5.0, end_time=10.0)
        clips = list_clips(proj, 0)
        assert len(clips) == 2
        assert clips[0]["name"] == "A"
        assert clips[1]["name"] == "B"
