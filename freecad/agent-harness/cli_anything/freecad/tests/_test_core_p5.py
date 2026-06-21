# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestSession:
    """Tests for the session module."""

    def test_status_no_project(self):
        session = Session()
        status = session.status()
        assert status["has_project"] is False
        assert status["project_path"] is None
        assert status["modified"] is False
        assert status["undo_depth"] == 0
        assert status["redo_depth"] == 0

        with pytest.raises(RuntimeError, match="No project"):
            session.get_project()

    def test_set_project(self):
        session = Session()
        proj = create_document(name="SessionTest")
        session.set_project(proj, path="/tmp/test.json")

        assert session.get_project()["name"] == "SessionTest"
        assert session.project_path == "/tmp/test.json"
        status = session.status()
        assert status["has_project"] is True
        assert status["modified"] is False

    def test_snapshot_and_undo(self):
        session = Session()
        proj = create_document(name="UndoTest")
        session.set_project(proj)

        # Take a snapshot, then mutate
        session.snapshot("before adding box")
        add_part(session.get_project(), "box", name="TempBox")
        assert len(session.get_project()["parts"]) == 1

        # Undo should restore the state before the mutation
        desc = session.undo()
        assert desc == "before adding box"
        assert len(session.get_project()["parts"]) == 0

        # Undo with empty stack returns None
        assert session.undo() is None

    def test_undo_redo_cycle(self):
        session = Session()
        proj = create_document(name="RedoTest")
        session.set_project(proj)

        # Snapshot -> mutate -> undo -> redo
        session.snapshot("add cylinder")
        add_part(session.get_project(), "cylinder", name="Cyl")
        assert len(session.get_project()["parts"]) == 1

        session.undo()
        assert len(session.get_project()["parts"]) == 0
        assert session.status()["redo_depth"] == 1

        desc = session.redo()
        assert desc == "add cylinder"
        assert len(session.get_project()["parts"]) == 1

        # Redo with empty stack returns None
        assert session.redo() is None

    def test_save_session(self, tmp_path):
        session = Session()
        proj = create_document(name="SaveTest")
        session.set_project(proj)

        filepath = str(tmp_path / "session_save.json")
        saved_path = session.save_session(path=filepath)
        assert os.path.isfile(saved_path)
        assert session.status()["modified"] is False

        # Verify the file contains valid JSON matching the project
        with open(saved_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["name"] == "SaveTest"

        # Save without path after initial save should use stored path
        session.snapshot("mark modified")
        saved_again = session.save_session()
        assert saved_again == saved_path

    def test_list_history(self):
        session = Session()
        proj = create_document(name="HistoryTest")
        session.set_project(proj)

        session.snapshot("step 1")
        add_part(session.get_project(), "box")
        session.snapshot("step 2")
        add_part(session.get_project(), "cylinder")
        session.snapshot("step 3")

        history = session.list_history()
        assert len(history) == 3
        # Newest first
        assert history[0]["description"] == "step 3"
        assert history[1]["description"] == "step 2"
        assert history[2]["description"] == "step 1"
        # Each entry has required keys
        for entry in history:
            assert "index" in entry
            assert "timestamp" in entry
            assert "description" in entry
