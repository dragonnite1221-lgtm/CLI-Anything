# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestSessionMixin1:
    def test_save_session_state(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_mod, "SESSION_DIR", tmp_path)
        s = Session("test_save_state")
        s.new_project()
        path = s.save_session_state()
        assert os.path.exists(path)
        state = json.load(open(path))
        assert state["session_id"] == "test_save_state"
        assert state["project_path"] is None
    def test_load_session_state(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_mod, "SESSION_DIR", tmp_path)
        s = Session("test_load")
        s.new_project()
        s.save_session_state()
        state = Session.load_session_state("test_load")
        assert state is not None
        assert state["session_id"] == "test_load"
    def test_load_session_state_nonexistent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_mod, "SESSION_DIR", tmp_path)
        assert Session.load_session_state("nonexistent") is None
    def test_list_sessions(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_mod, "SESSION_DIR", tmp_path)
        s1 = Session("list_s1")
        s1.new_project()
        s1.save_session_state()
        s2 = Session("list_s2")
        s2.new_project()
        s2.save_session_state()
        sessions = Session.list_sessions()
        assert len(sessions) >= 2
        ids = {s["session_id"] for s in sessions}
        assert "list_s1" in ids
        assert "list_s2" in ids
    def test_get_profile(self):
        s = Session()
        s.new_project()
        prof = s.get_profile()
        assert prof["width"] == "1920"
        assert prof["height"] == "1080"
    def test_get_profile_no_project(self):
        with pytest.raises(RuntimeError):
            Session().get_profile()
    def test_save_no_path(self):
        s = Session()
        s.new_project()
        with pytest.raises(RuntimeError, match="No save path"):
            s.save_project()
    def test_get_profile_no_profile_element(self, tmp_path):
        s = Session()
        root = ET.Element("mlt")
        s.root = root
        s._resolve_refs()
        prof = s.get_profile()
        assert prof == {}
    def test_snapshot_no_project(self):
        s = Session()
        assert s._snapshot() == b""
    def test_max_undo_depth(self):
        s = Session()
        s.new_project()
        for _ in range(55):
            s.checkpoint()
        assert len(s._undo_stack) <= session_mod.MAX_UNDO_DEPTH
    def test_list_sessions_handles_corrupt(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_mod, "SESSION_DIR", tmp_path)
        corrupt = tmp_path / "bad.json"
        corrupt.write_text("not valid json{{{")
        sessions = Session.list_sessions()
        assert isinstance(sessions, list)
    def test_undo_restores_clip_state(self, session_with_track, dummy_file):
        media_mod.import_media(session_with_track, dummy_file)
        assert len(session_with_track._bin_chains) == 1
        session_with_track.undo()
        assert len(session_with_track._bin_chains) == 0
