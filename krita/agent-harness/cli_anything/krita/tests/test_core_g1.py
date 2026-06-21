# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_session_snapshot(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "initial")
        assert len(sess.history()) == 1

    def test_session_undo(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "state1")
        modified = copy.deepcopy(sample_project)
        modified["name"] = "Modified"
        sess.snapshot(modified, "state2")
        restored = sess.undo()
        assert restored is not None
        assert restored["name"] == "Test"

    def test_session_redo(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "state1")
        modified = copy.deepcopy(sample_project)
        modified["name"] = "Modified"
        sess.snapshot(modified, "state2")
        sess.undo()
        restored = sess.redo()
        assert restored is not None
        assert restored["name"] == "Modified"

    def test_session_undo_at_start(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "only")
        result = sess.undo()
        assert result is None

    def test_session_redo_at_end(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "only")
        result = sess.redo()
        assert result is None

    def test_session_branch_discards_redo(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "s1")
        m1 = copy.deepcopy(sample_project)
        m1["name"] = "M1"
        sess.snapshot(m1, "s2")
        m2 = copy.deepcopy(sample_project)
        m2["name"] = "M2"
        sess.snapshot(m2, "s3")
        sess.undo()  # back to s2
        sess.undo()  # back to s1
        branch = copy.deepcopy(sample_project)
        branch["name"] = "Branch"
        sess.snapshot(branch, "branch")
        assert len(sess.history()) == 2  # s1 + branch
        assert sess.redo() is None

    def test_session_history(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "a")
        sess.snapshot(sample_project, "b")
        sess.snapshot(sample_project, "c")
        hist = sess.history()
        assert len(hist) == 3

    def test_session_save_load(self, tmp_dir, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "saved")
        path = os.path.join(tmp_dir, "session.json")
        sess.save(path)
        assert os.path.exists(path)
        sess2 = Session()
        sess2.load(path)
        assert len(sess2.history()) == 1

    def test_session_clear(self, sample_project):
        sess = Session()
        sess.snapshot(sample_project, "a")
        sess.snapshot(sample_project, "b")
        sess.clear()
        assert len(sess.history()) == 0

    def test_session_can_undo_redo(self, sample_project):
        sess = Session()
        assert sess.can_undo() is False
        assert sess.can_redo() is False
        sess.snapshot(sample_project, "s1")
        assert sess.can_undo() is False  # only one state
        m = copy.deepcopy(sample_project)
        m["name"] = "m"
        sess.snapshot(m, "s2")
        assert sess.can_undo() is True
        assert sess.can_redo() is False
        sess.undo()
        assert sess.can_redo() is True
