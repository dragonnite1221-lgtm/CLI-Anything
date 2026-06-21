# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTransitions:
    def _make_project(self):
        return create_project()

    def test_add_transition(self):
        proj = self._make_project()
        trans = add_transition(proj, "swipe")
        assert trans["type"] == "swipe"
        assert len(proj["transitions"]) == 3

    def test_add_transition_with_duration(self):
        proj = self._make_project()
        trans = add_transition(proj, "fade", duration=500)
        assert trans["duration"] == 500

    def test_add_transition_invalid_type(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="Unknown transition type"):
            add_transition(proj, "nonexistent")

    def test_add_transition_negative_duration(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="non-negative"):
            add_transition(proj, "fade", duration=-1)

    def test_remove_transition(self):
        proj = self._make_project()
        removed = remove_transition(proj, 1)
        assert removed["type"] == "fade"
        assert len(proj["transitions"]) == 1

    def test_remove_last_transition_fails(self):
        proj = self._make_project()
        remove_transition(proj, 1)
        with pytest.raises(ValueError, match="Cannot remove the last"):
            remove_transition(proj, 0)

    def test_set_duration(self):
        proj = self._make_project()
        trans = set_duration(proj, 1, 1000)
        assert trans["duration"] == 1000

    def test_set_duration_negative(self):
        proj = self._make_project()
        with pytest.raises(ValueError, match="non-negative"):
            set_duration(proj, 1, -1)

    def test_set_active_transition(self):
        proj = self._make_project()
        result = set_active_transition(proj, 1)
        assert result["index"] == 1
        assert proj["active_transition"] == 1

    def test_list_transitions(self):
        proj = self._make_project()
        result = list_transitions(proj)
        assert len(result) == 2
        assert result[0]["type"] == "cut"
        assert result[1]["type"] == "fade"

    def test_all_transition_types(self):
        proj = self._make_project()
        for ttype in TRANSITION_TYPES:
            trans = add_transition(proj, ttype)
            assert trans["type"] == ttype
