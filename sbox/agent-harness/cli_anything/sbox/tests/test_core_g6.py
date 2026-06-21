# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    """Tests for cli_anything.sbox.core.session."""

    def test_session_create(self, tmp_path):
        """Create a new session."""
        session_path = str(tmp_path / "session.json")
        session = Session(session_path=session_path)

        status = session.get_status()
        assert status["project_path"] is None
        assert status["scene_path"] is None
        assert status["undo_count"] == 0
        assert status["redo_count"] == 0

    def test_session_set_project(self, tmp_path):
        """Set project path."""
        session_path = str(tmp_path / "session.json")
        session = Session(session_path=session_path)

        # Create a dummy sbproj to reference
        dummy_proj = tmp_path / "test.sbproj"
        dummy_proj.write_text("{}", encoding="utf-8")

        session.set_project(str(dummy_proj))
        assert session.project_path == str(dummy_proj.resolve())

        # Verify persistence by creating a new Session from the same file
        session2 = Session(session_path=session_path)
        assert session2.project_path == str(dummy_proj.resolve())

    def test_session_undo_redo(self, tmp_path):
        """Record ops, undo, redo."""
        session_path = str(tmp_path / "session.json")
        session = Session(session_path=session_path)

        # Record two operations
        session.record_operation(
            op_type="scene_modify",
            description="Added turret",
            before_state={"count": 0},
            after_state={"count": 1},
        )
        session.record_operation(
            op_type="scene_modify",
            description="Added wall",
            before_state={"count": 1},
            after_state={"count": 2},
        )

        status = session.get_status()
        assert status["undo_count"] == 2
        assert status["redo_count"] == 0

        # Undo last operation
        undone = session.undo()
        assert undone is not None
        assert undone["undone"] is True
        assert undone["description"] == "Added wall"
        assert undone["before_state"] == {"count": 1}

        status = session.get_status()
        assert status["undo_count"] == 1
        assert status["redo_count"] == 1

        # Redo it
        redone = session.redo()
        assert redone is not None
        assert redone["redone"] is True
        assert redone["description"] == "Added wall"

        status = session.get_status()
        assert status["undo_count"] == 2
        assert status["redo_count"] == 0

        # Undo when stack is empty after undoing everything
        session.undo()
        session.undo()
        result = session.undo()
        assert result is None

    def test_session_save_load(self, tmp_path):
        """Save and reload session."""
        session_path = str(tmp_path / "session.json")
        session = Session(session_path=session_path)

        dummy_proj = tmp_path / "test.sbproj"
        dummy_proj.write_text("{}", encoding="utf-8")
        dummy_scene = tmp_path / "test.scene"
        dummy_scene.write_text("{}", encoding="utf-8")

        session.set_project(str(dummy_proj))
        session.set_scene(str(dummy_scene))
        session.record_operation(
            op_type="codegen",
            description="Generated component",
        )

        # Create a fresh Session from the same path
        session2 = Session(session_path=session_path)
        status = session2.get_status()
        assert status["project_path"] == str(dummy_proj.resolve())
        assert status["scene_path"] == str(dummy_scene.resolve())
        assert status["undo_count"] == 1

    def test_session_clear(self, tmp_path):
        """Clear session state."""
        session_path = str(tmp_path / "session.json")
        session = Session(session_path=session_path)

        dummy_proj = tmp_path / "test.sbproj"
        dummy_proj.write_text("{}", encoding="utf-8")
        session.set_project(str(dummy_proj))
        session.record_operation(
            op_type="scene_modify",
            description="Test op",
        )

        session.clear()

        status = session.get_status()
        assert status["project_path"] is None
        assert status["scene_path"] is None
        assert status["undo_count"] == 0
        assert status["redo_count"] == 0

    def test_session_load_corrupt_file_warns_and_preserves_backup(
        self, tmp_path, capsys
    ):
        """A malformed session file is preserved as .corrupt.<ts> and warned about.

        Reset must not be silent: the user's undo history could otherwise be
        destroyed without any signal. The backup uses a timestamp suffix so a
        second corruption does not silently overwrite the first.
        """
        session_path = tmp_path / "session.json"
        session_path.write_text("not valid json{{{", encoding="utf-8")

        session = Session(session_path=str(session_path))

        captured = capsys.readouterr()
        assert "could not be read" in captured.err
        assert "preserved as" in captured.err

        # Original file moved aside
        assert not session_path.exists()

        # Backup exists with timestamp suffix and contains the original bytes
        backups = list(tmp_path.glob("session.json.corrupt.*"))
        assert len(backups) == 1
        assert backups[0].read_text(encoding="utf-8") == "not valid json{{{"

        # Session is reset to empty state
        assert session.get_status()["project_path"] is None
