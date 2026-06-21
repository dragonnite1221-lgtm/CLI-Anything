# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTimeline:
    def _make_project_with_clip(self):
        proj = create_project()
        import_clip(proj, "/video.mp4", name="TestClip", duration=30.0)
        return proj

    def test_add_video_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj, track_type="video")
        assert track["type"] == "video"
        assert track["name"] == "V1"
        assert len(proj["tracks"]) == 1

    def test_add_audio_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj, track_type="audio")
        assert track["type"] == "audio"
        assert track["name"] == "A1"

    def test_add_track_custom_name(self):
        proj = self._make_project_with_clip()
        track = add_track(proj, name="MyTrack")
        assert track["name"] == "MyTrack"

    def test_add_track_invalid_type(self):
        proj = self._make_project_with_clip()
        with pytest.raises(ValueError, match="Invalid track type"):
            add_track(proj, track_type="invalid")

    def test_remove_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        removed = remove_track(proj, track["id"])
        assert removed["name"] == track["name"]
        assert len(proj["tracks"]) == 0

    def test_remove_track_not_found(self):
        proj = self._make_project_with_clip()
        with pytest.raises(ValueError, match="Track not found"):
            remove_track(proj, 999)

    def test_add_clip_to_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        entry = add_clip_to_track(
            proj, track["id"], "clip0", position=0.0, in_point=0.0, out_point=10.0
        )
        assert entry["clip_id"] == "clip0"
        assert entry["position"] == 0.0
        assert entry["in"] == 0.0
        assert entry["out"] == 10.0

    def test_add_clip_to_track_auto_out(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        entry = add_clip_to_track(proj, track["id"], "clip0")
        assert entry["out"] == 30.0  # full clip duration

    def test_add_clip_invalid_clip_id(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        with pytest.raises(ValueError, match="Clip not found"):
            add_clip_to_track(proj, track["id"], "nonexistent")

    def test_add_clip_locked_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj, locked=True)
        with pytest.raises(RuntimeError, match="locked"):
            add_clip_to_track(proj, track["id"], "clip0")

    def test_add_clip_invalid_in_out(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        with pytest.raises(ValueError, match="greater than in-point"):
            add_clip_to_track(proj, track["id"], "clip0", in_point=10.0, out_point=5.0)

    def test_remove_clip_from_track(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=10.0)
        removed = remove_clip_from_track(proj, track["id"], 0)
        assert removed["clip_id"] == "clip0"
        assert len(proj["tracks"][0]["clips"]) == 0

    def test_remove_clip_from_track_empty(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        with pytest.raises(ValueError, match="No clips"):
            remove_clip_from_track(proj, track["id"], 0)

    def test_trim_clip(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=20.0)
        result = trim_clip(proj, track["id"], 0, new_in=5.0, new_out=15.0)
        assert result["in"] == 5.0
        assert result["out"] == 15.0

    def test_trim_clip_invalid(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=20.0)
        with pytest.raises(ValueError, match="greater than in-point"):
            trim_clip(proj, track["id"], 0, new_in=20.0, new_out=5.0)

    def test_split_clip(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=20.0)
        parts = split_clip(proj, track["id"], 0, split_at=10.0)
        assert len(parts) == 2
        assert parts[0]["out"] == 10.0
        assert parts[1]["in"] == 10.0
        assert len(proj["tracks"][0]["clips"]) == 2

    def test_split_clip_at_boundary(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=20.0)
        with pytest.raises(ValueError, match="Split point"):
            split_clip(proj, track["id"], 0, split_at=0.0)

    def test_split_clip_beyond_duration(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=20.0)
        with pytest.raises(ValueError, match="Split point"):
            split_clip(proj, track["id"], 0, split_at=25.0)

    def test_move_clip(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", position=0.0, out_point=10.0)
        result = move_clip(proj, track["id"], 0, new_position=5.0)
        assert result["position"] == 5.0

    def test_move_clip_negative(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", out_point=10.0)
        with pytest.raises(ValueError, match="non-negative"):
            move_clip(proj, track["id"], 0, new_position=-1.0)

    def test_list_tracks(self):
        proj = self._make_project_with_clip()
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")
        tracks = list_tracks(proj)
        assert len(tracks) == 2

    def test_clips_sorted_by_position(self):
        proj = self._make_project_with_clip()
        track = add_track(proj)
        add_clip_to_track(proj, track["id"], "clip0", position=10.0, out_point=15.0)
        add_clip_to_track(proj, track["id"], "clip0", position=0.0, out_point=5.0)
        clips = proj["tracks"][0]["clips"]
        assert clips[0]["position"] <= clips[1]["position"]
