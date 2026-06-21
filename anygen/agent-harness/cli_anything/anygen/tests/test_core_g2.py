# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_record_and_history(self):
        sess = Session()
        sess.record("task create", {"op": "slide"}, {"task_id": "t1"})
        sess.record("task poll", {"id": "t1"})
        h = sess.history()
        assert len(h) == 2
        assert h[0]["command"] == "task create"

    def test_undo(self):
        sess = Session()
        sess.record("cmd1", {})
        sess.record("cmd2", {})
        entry = sess.undo()
        assert entry.command == "cmd2"
        assert sess.history_count == 1

    def test_redo(self):
        sess = Session()
        sess.record("cmd1", {})
        sess.undo()
        entry = sess.redo()
        assert entry.command == "cmd1"
        assert sess.history_count == 1

    def test_undo_clears_redo_on_record(self):
        sess = Session()
        sess.record("cmd1", {})
        sess.undo()
        sess.record("cmd2", {})
        assert not sess.can_redo

    def test_undo_empty(self):
        sess = Session()
        assert sess.undo() is None

    def test_redo_empty(self):
        sess = Session()
        assert sess.redo() is None

    def test_history_limit(self):
        sess = Session()
        for i in range(30):
            sess.record(f"cmd{i}", {})
        assert len(sess.history(limit=5)) == 5

    def test_status(self):
        sess = Session()
        sess.record("cmd1", {})
        st = sess.status()
        assert st["history_count"] == 1
        assert st["can_undo"] is True
        assert st["can_redo"] is False

    def test_save_and_load(self, tmp_path):
        path = str(tmp_path / "session.json")
        sess = Session()
        sess.record("cmd1", {"a": 1}, {"r": "ok"})
        sess.save(path)

        sess2 = Session(session_file=path)
        h = sess2.history()
        assert len(h) == 1
        assert h[0]["command"] == "cmd1"

    def test_load_corrupt_file(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json")
        sess = Session(session_file=str(path))
        assert sess.history_count == 0
