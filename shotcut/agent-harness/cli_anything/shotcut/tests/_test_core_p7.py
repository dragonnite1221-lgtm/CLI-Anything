# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCompositing:
    def test_list_blend_modes(self):
        result = comp_mod.list_blend_modes()
        names = [m["name"] for m in result]
        assert len(result) >= 18
        assert "normal" in names
        assert "multiply" in names

    def test_set_track_blend_mode(self, session_with_two_tracks):
        result = comp_mod.set_track_blend_mode(session_with_two_tracks, 2, "multiply")
        assert result["blend_mode"] == "multiply"

    def test_set_blend_mode_invalid(self, session_with_two_tracks):
        with pytest.raises(ValueError):
            comp_mod.set_track_blend_mode(session_with_two_tracks, 2, "nonexistent_mode")

    def test_set_blend_mode_background_track(self, session_with_two_tracks):
        with pytest.raises(ValueError):
            comp_mod.set_track_blend_mode(session_with_two_tracks, 0, "multiply")

    def test_get_track_blend_mode_default(self, session_with_two_tracks):
        assert comp_mod.get_track_blend_mode(session_with_two_tracks, 2)["blend_mode"] == "normal"

    def test_get_track_blend_mode_after_set(self, session_with_two_tracks):
        comp_mod.set_track_blend_mode(session_with_two_tracks, 2, "screen")
        assert comp_mod.get_track_blend_mode(session_with_two_tracks, 2)["blend_mode"] == "screen"

    def test_set_track_opacity(self, session_with_two_tracks):
        result = comp_mod.set_track_opacity(session_with_two_tracks, 1, 0.5)
        assert result["opacity"] == 0.5

    def test_set_track_opacity_invalid_range(self, session_with_two_tracks):
        with pytest.raises(ValueError):
            comp_mod.set_track_opacity(session_with_two_tracks, 1, 1.5)
        with pytest.raises(ValueError):
            comp_mod.set_track_opacity(session_with_two_tracks, 1, -0.1)

    def test_set_track_opacity_invalid_index(self, session_with_two_tracks):
        with pytest.raises(IndexError):
            comp_mod.set_track_opacity(session_with_two_tracks, 99, 0.5)

    def test_set_track_opacity_update_existing(self, session_with_two_tracks):
        comp_mod.set_track_opacity(session_with_two_tracks, 1, 0.5)
        assert comp_mod.set_track_opacity(session_with_two_tracks, 1, 0.8)["opacity"] == 0.8

    def test_pip_position(self, session_with_two_tracks):
        result = comp_mod.pip_position(session_with_two_tracks, 2, 0,
                                       x="10%", y="10%", width="40%", height="40%", opacity=0.9)
        assert result["geometry"] == "10%/10%:40%x40%:90"

    def test_pip_position_defaults(self, session_with_two_tracks):
        result = comp_mod.pip_position(session_with_two_tracks, 2, 0)
        assert result["geometry"] == "0/0:100%x100%:100"

    def test_pip_position_invalid_track(self, session_with_two_tracks):
        with pytest.raises(IndexError):
            comp_mod.pip_position(session_with_two_tracks, 99, 0)

    def test_pip_position_invalid_clip(self, session_with_two_tracks):
        with pytest.raises(IndexError):
            comp_mod.pip_position(session_with_two_tracks, 2, 99)

    def test_pip_update_existing(self, session_with_two_tracks):
        comp_mod.pip_position(session_with_two_tracks, 2, 0,
                              x="10%", y="10%", width="40%", height="40%")
        result = comp_mod.pip_position(session_with_two_tracks, 2, 0,
                                       x="20%", y="20%", width="50%", height="50%")
        assert result["geometry"] == "20%/20%:50%x50%:100"

    def test_undo_set_blend_mode(self, session_with_two_tracks):
        comp_mod.set_track_blend_mode(session_with_two_tracks, 2, "multiply")
        assert comp_mod.get_track_blend_mode(session_with_two_tracks, 2)["blend_mode"] == "multiply"
        session_with_two_tracks.undo()
        assert comp_mod.get_track_blend_mode(session_with_two_tracks, 2)["blend_mode"] == "normal"

    def test_blend_mode_replaces_qtblend_with_cairolend(self, session_with_two_tracks):
        tractor = session_with_two_tracks.get_main_tractor()
        comp_trans = [t for t in tractor.findall("transition")
                      if get_property(t, "mlt_service") == "qtblend"
                      and get_property(t, "b_track") == "2"]
        assert len(comp_trans) == 1
        comp_mod.set_track_blend_mode(session_with_two_tracks, 2, "multiply")
        services = [get_property(t, "mlt_service") for t in tractor.findall("transition")]
        assert "frei0r.cairoblend" in services
        assert not any(get_property(t, "mlt_service") == "qtblend"
                       and get_property(t, "b_track") == "2"
                       for t in tractor.findall("transition"))

    def test_blend_mode_re_enables_first_video_track(self, session_with_track):
        comp_mod.set_track_blend_mode(session_with_track, 1, "multiply")
        tractor = session_with_track.get_main_tractor()
        for trans in tractor.findall("transition"):
            if (get_property(trans, "mlt_service") == "frei0r.cairoblend"
                    and get_property(trans, "b_track") == "1"):
                assert get_property(trans, "disable", "0") == "0"
                return
        pytest.fail("No cairolend transition found for track 1")

    def test_remove_lower_video_track_disables_qtblend(self, session):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "video", "V2")
        tl_mod.remove_track(session, 1)
        for trans in session.get_main_tractor().findall("transition"):
            if get_property(trans, "mlt_service") == "qtblend":
                assert get_property(trans, "disable", "0") == "1"
