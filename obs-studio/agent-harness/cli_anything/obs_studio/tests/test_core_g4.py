# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAudio:
    def _make_project(self):
        return create_project()

    def test_add_audio_source(self):
        proj = self._make_project()
        src = add_audio_source(proj, name="Mic")
        assert src["name"] == "Mic"
        assert src["type"] == "input"
        assert len(proj["audio_sources"]) == 1

    def test_add_audio_output(self):
        proj = self._make_project()
        src = add_audio_source(proj, name="Desktop", audio_type="output")
        assert src["type"] == "output"

    def test_add_audio_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Invalid audio type"):
            add_audio_source(proj, audio_type="bogus")

    def test_set_volume(self):
        proj = self._make_project()
        add_audio_source(proj)
        src = set_volume(proj, 0, 0.5)
        assert src["volume"] == 0.5

    def test_set_volume_out_of_range(self):
        proj = self._make_project()
        add_audio_source(proj)
        with pytest.raises(ValueError, match="must be between"):
            set_volume(proj, 0, 5.0)

    def test_mute(self):
        proj = self._make_project()
        add_audio_source(proj)
        src = mute(proj, 0)
        assert src["muted"] is True

    def test_unmute(self):
        proj = self._make_project()
        add_audio_source(proj, muted=True)
        src = unmute(proj, 0)
        assert src["muted"] is False

    def test_set_monitor(self):
        proj = self._make_project()
        add_audio_source(proj)
        src = set_monitor(proj, 0, "monitor_only")
        assert src["monitor"] == "monitor_only"

    def test_set_monitor_invalid(self):
        proj = self._make_project()
        add_audio_source(proj)
        with pytest.raises(ValueError, match="Invalid monitor type"):
            set_monitor(proj, 0, "bogus")

    def test_set_balance(self):
        proj = self._make_project()
        add_audio_source(proj)
        src = set_balance(proj, 0, -0.5)
        assert src["balance"] == -0.5

    def test_set_sync_offset(self):
        proj = self._make_project()
        add_audio_source(proj)
        src = set_sync_offset(proj, 0, 100)
        assert src["sync_offset"] == 100

    def test_remove_audio(self):
        proj = self._make_project()
        add_audio_source(proj, name="Mic")
        removed = remove_audio_source(proj, 0)
        assert removed["name"] == "Mic"

    def test_list_audio(self):
        proj = self._make_project()
        add_audio_source(proj, name="Mic")
        add_audio_source(proj, name="Desktop", audio_type="output")
        result = list_audio(proj)
        assert len(result) == 2

    def test_audio_unique_names(self):
        proj = self._make_project()
        a1 = add_audio_source(proj, name="Mic")
        a2 = add_audio_source(proj, name="Mic")
        assert a1["name"] != a2["name"]
