# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTracks:
    def _make_project(self):
        return create_project()

    def test_add_track(self):
        proj = self._make_project()
        track = add_track(proj, name="Voice")
        assert track["name"] == "Voice"
        assert track["type"] == "audio"
        assert len(proj["tracks"]) == 1

    def test_add_track_default_name(self):
        proj = self._make_project()
        track = add_track(proj)
        assert track["name"] == "Track 0"

    def test_add_multiple_tracks(self):
        proj = self._make_project()
        add_track(proj, name="Track A")
        add_track(proj, name="Track B")
        add_track(proj, name="Track C")
        assert len(proj["tracks"]) == 3

    def test_add_track_with_volume_pan(self):
        proj = self._make_project()
        track = add_track(proj, volume=0.8, pan=-0.5)
        assert track["volume"] == 0.8
        assert track["pan"] == -0.5

    def test_add_track_invalid_volume(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Volume"):
            add_track(proj, volume=3.0)

    def test_add_track_invalid_pan(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Pan"):
            add_track(proj, pan=2.0)

    def test_add_track_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid track type"):
            add_track(proj, track_type="video")

    def test_remove_track(self):
        proj = self._make_project()
        add_track(proj, name="To Remove")
        removed = remove_track(proj, 0)
        assert removed["name"] == "To Remove"
        assert len(proj["tracks"]) == 0

    def test_remove_track_out_of_range(self):
        proj = self._make_project()
        with pytest.raises(IndexError):
            remove_track(proj, 0)

    def test_get_track(self):
        proj = self._make_project()
        add_track(proj, name="Test")
        track = get_track(proj, 0)
        assert track["name"] == "Test"

    def test_set_track_name(self):
        proj = self._make_project()
        add_track(proj, name="Old")
        set_track_property(proj, 0, "name", "New")
        assert proj["tracks"][0]["name"] == "New"

    def test_set_track_mute(self):
        proj = self._make_project()
        add_track(proj)
        set_track_property(proj, 0, "mute", "true")
        assert proj["tracks"][0]["mute"] is True

    def test_set_track_solo(self):
        proj = self._make_project()
        add_track(proj)
        set_track_property(proj, 0, "solo", "true")
        assert proj["tracks"][0]["solo"] is True

    def test_set_track_volume(self):
        proj = self._make_project()
        add_track(proj)
        set_track_property(proj, 0, "volume", "0.5")
        assert proj["tracks"][0]["volume"] == 0.5

    def test_set_track_invalid_prop(self):
        proj = self._make_project()
        add_track(proj)
        with pytest.raises(ValueError, match="Unknown track property"):
            set_track_property(proj, 0, "color", "red")

    def test_list_tracks(self):
        proj = self._make_project()
        add_track(proj, name="A")
        add_track(proj, name="B")
        tracks = list_tracks(proj)
        assert len(tracks) == 2
        assert tracks[0]["name"] == "A"
        assert tracks[1]["name"] == "B"
