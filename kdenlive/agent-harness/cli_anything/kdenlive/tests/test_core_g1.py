# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBin:
    def _make_project(self):
        return create_project()

    def test_import_clip(self):
        proj = self._make_project()
        clip = import_clip(proj, "/path/to/video.mp4", name="Interview", duration=120.5)
        assert clip["name"] == "Interview"
        assert clip["source"] == "/path/to/video.mp4"
        assert clip["duration"] == 120.5
        assert clip["type"] == "video"
        assert len(proj["bin"]) == 1

    def test_import_clip_auto_name(self):
        proj = self._make_project()
        clip = import_clip(proj, "/path/to/my_video.mp4")
        assert clip["name"] == "my_video"

    def test_import_clip_types(self):
        proj = self._make_project()
        for ct in CLIP_TYPES:
            clip = import_clip(proj, f"/path/{ct}.file", clip_type=ct)
            assert clip["type"] == ct

    def test_import_clip_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid clip type"):
            import_clip(proj, "/path/file.mp4", clip_type="invalid")

    def test_import_clip_negative_duration(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="non-negative"):
            import_clip(proj, "/path/file.mp4", duration=-1.0)

    def test_unique_clip_ids(self):
        proj = self._make_project()
        c1 = import_clip(proj, "/a.mp4")
        c2 = import_clip(proj, "/b.mp4")
        assert c1["id"] != c2["id"]

    def test_unique_clip_names(self):
        proj = self._make_project()
        c1 = import_clip(proj, "/a.mp4", name="Clip")
        c2 = import_clip(proj, "/b.mp4", name="Clip")
        assert c1["name"] != c2["name"]

    def test_remove_clip(self):
        proj = self._make_project()
        clip = import_clip(proj, "/a.mp4", name="Test")
        removed = remove_clip(proj, clip["id"])
        assert removed["name"] == "Test"
        assert len(proj["bin"]) == 0

    def test_remove_clip_not_found(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Clip not found"):
            remove_clip(proj, "nonexistent")

    def test_list_clips(self):
        proj = self._make_project()
        import_clip(proj, "/a.mp4", name="A")
        import_clip(proj, "/b.mp4", name="B")
        clips = list_clips(proj)
        assert len(clips) == 2

    def test_get_clip(self):
        proj = self._make_project()
        clip = import_clip(proj, "/a.mp4", name="Test")
        fetched = get_clip(proj, clip["id"])
        assert fetched["name"] == "Test"

    def test_get_clip_not_found(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Clip not found"):
            get_clip(proj, "nonexistent")
