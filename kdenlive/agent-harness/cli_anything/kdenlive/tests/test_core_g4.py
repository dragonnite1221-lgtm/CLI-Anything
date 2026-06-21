# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTransitions:
    def _make_project_with_tracks(self):
        proj = create_project()
        add_track(proj, track_type="video")
        add_track(proj, track_type="video")
        return proj

    def test_add_dissolve(self):
        proj = self._make_project_with_tracks()
        t = add_transition(proj, "dissolve", 0, 1, position=5.0, duration=1.0)
        assert t["type"] == "dissolve"
        assert t["track_a"] == 0
        assert t["track_b"] == 1

    def test_add_transition_unknown(self):
        proj = self._make_project_with_tracks()
        with pytest.raises(ValueError, match="Unknown transition type"):
            add_transition(proj, "nonexistent", 0, 1)

    def test_add_transition_same_track(self):
        proj = self._make_project_with_tracks()
        with pytest.raises(ValueError, match="different tracks"):
            add_transition(proj, "dissolve", 0, 0)

    def test_add_transition_invalid_track(self):
        proj = self._make_project_with_tracks()
        with pytest.raises(ValueError, match="Track not found"):
            add_transition(proj, "dissolve", 0, 99)

    def test_remove_transition(self):
        proj = self._make_project_with_tracks()
        t = add_transition(proj, "dissolve", 0, 1)
        removed = remove_transition(proj, t["id"])
        assert removed["type"] == "dissolve"
        assert len(proj["transitions"]) == 0

    def test_remove_transition_not_found(self):
        proj = self._make_project_with_tracks()
        with pytest.raises(ValueError, match="Transition not found"):
            remove_transition(proj, 999)

    def test_set_transition_param(self):
        proj = self._make_project_with_tracks()
        t = add_transition(proj, "dissolve", 0, 1)
        result = set_transition(proj, t["id"], "softness", 0.5)
        assert result["params"]["softness"] == 0.5

    def test_set_transition_position(self):
        proj = self._make_project_with_tracks()
        t = add_transition(proj, "dissolve", 0, 1)
        result = set_transition(proj, t["id"], "position", 10.0)
        assert result["position"] == 10.0

    def test_set_transition_duration(self):
        proj = self._make_project_with_tracks()
        t = add_transition(proj, "dissolve", 0, 1)
        result = set_transition(proj, t["id"], "duration", 2.5)
        assert result["duration"] == 2.5

    def test_list_transitions(self):
        proj = self._make_project_with_tracks()
        add_transition(proj, "dissolve", 0, 1)
        add_transition(proj, "wipe", 0, 1, position=10.0)
        transitions = list_transitions(proj)
        assert len(transitions) == 2

    def test_all_transition_types_have_mlt_service(self):
        for name, spec in TRANSITION_TYPES.items():
            assert "mlt_service" in spec
            assert spec["mlt_service"]
