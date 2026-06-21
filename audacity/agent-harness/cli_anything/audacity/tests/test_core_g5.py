# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_no_project(self):
        sess = Session()
        assert not sess.has_project()
        with pytest.raises(RuntimeError, match="No project loaded"):
            sess.get_project()

    def test_set_project(self):
        sess = Session()
        proj = create_project(name="test")
        sess.set_project(proj)
        assert sess.has_project()
        assert sess.get_project()["name"] == "test"

    def test_undo_empty(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            sess.undo()

    def test_redo_empty(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            sess.redo()

    def test_undo_redo_cycle(self):
        sess = Session()
        proj = create_project(name="original")
        sess.set_project(proj)

        sess.snapshot("Rename")
        proj["name"] = "changed"
        assert sess.get_project()["name"] == "changed"

        sess.undo()
        assert sess.get_project()["name"] == "original"

        sess.redo()
        assert sess.get_project()["name"] == "changed"

    def test_multiple_undos(self):
        sess = Session()
        proj = create_project(name="v0")
        sess.set_project(proj)

        sess.snapshot("v1")
        proj["name"] = "v1"
        sess.snapshot("v2")
        proj["name"] = "v2"
        sess.snapshot("v3")
        proj["name"] = "v3"

        assert sess.get_project()["name"] == "v3"
        sess.undo()
        assert sess.get_project()["name"] == "v2"
        sess.undo()
        assert sess.get_project()["name"] == "v1"
        sess.undo()
        assert sess.get_project()["name"] == "v0"

    def test_status(self):
        sess = Session()
        proj = create_project(name="status_test")
        sess.set_project(proj)
        status = sess.status()
        assert status["has_project"] is True
        assert status["project_name"] == "status_test"
        assert status["undo_count"] == 0

    def test_save_session(self):
        sess = Session()
        proj = create_project(name="save_test")
        sess.set_project(proj)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            saved = sess.save_session(path)
            assert os.path.exists(saved)
            loaded = open_project(saved)
            assert loaded["name"] == "save_test"
        finally:
            os.unlink(path)

    def test_save_session_no_path(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)
        with pytest.raises(ValueError, match="No save path"):
            sess.save_session()

    def test_list_history(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)
        sess.snapshot("Action 1")
        sess.snapshot("Action 2")
        history = sess.list_history()
        assert len(history) == 2
        assert history[0]["description"] == "Action 2"
        assert history[1]["description"] == "Action 1"

    def test_snapshot_clears_redo(self):
        sess = Session()
        proj = create_project(name="v0")
        sess.set_project(proj)
        sess.snapshot("v1")
        proj["name"] = "v1"
        sess.undo()
        # Now redo is available
        assert sess.status()["redo_count"] == 1
        # New snapshot should clear redo
        sess.snapshot("v2")
        assert sess.status()["redo_count"] == 0
