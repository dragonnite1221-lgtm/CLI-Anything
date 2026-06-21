# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_new_session(self):
        s = Session()
        assert s.session_id.startswith("session_")
        assert not s.is_open
        assert not s.is_modified

    def test_new_session_with_id(self):
        s = Session("my_session")
        assert s.session_id == "my_session"

    def test_new_project(self):
        s = Session()
        s.new_project()
        assert s.is_open
        assert not s.is_modified
        assert s.editor["aspectRatio"] == "16:9"
        assert s.editor["padding"] == 50

    def test_new_project_with_video(self):
        s = Session()
        s.new_project("/tmp/test.mp4")
        assert s.is_open
        assert s.data["media"]["screenVideoPath"] == "/tmp/test.mp4"

    def test_undo_redo(self):
        s = Session()
        s.new_project()
        # No undo available on fresh project
        assert not s.undo()

        # Make a change
        s.checkpoint()
        s.editor["padding"] = 30

        # Undo should restore
        assert s.undo()
        assert s.editor["padding"] == 50

        # Redo should reapply
        assert s.redo()
        assert s.editor["padding"] == 30

    def test_undo_clears_redo(self):
        s = Session()
        s.new_project()

        s.checkpoint()
        s.editor["padding"] = 30

        s.checkpoint()
        s.editor["padding"] = 20

        assert s.undo()
        assert s.editor["padding"] == 30

        # New change should clear redo stack
        s.checkpoint()
        s.editor["padding"] = 40
        assert not s.redo()

    def test_save_load_project(self):
        s = Session()
        s.new_project()
        s.checkpoint()
        s.editor["padding"] = 42

        with tempfile.NamedTemporaryFile(suffix=".openscreen", delete=False) as f:
            path = f.name

        try:
            s.save_project(path)
            assert not s.is_modified

            s2 = Session()
            s2.open_project(path)
            assert s2.is_open
            assert s2.editor["padding"] == 42
        finally:
            os.unlink(path)

    def test_open_nonexistent(self):
        s = Session()
        with pytest.raises(FileNotFoundError):
            s.open_project("/nonexistent/project.openscreen")

    def test_save_without_path(self):
        s = Session()
        s.new_project()
        with pytest.raises(RuntimeError, match="No save path"):
            s.save_project()

    def test_status(self):
        s = Session()
        status = s.status()
        assert status["project_open"] is False

        s.new_project()
        status = s.status()
        assert status["project_open"] is True
        assert status["zoom_region_count"] == 0

    # ── Extra tests from auto version ──────────────────────────────────

    def test_editor_raises_when_not_open(self):
        s = Session()
        with pytest.raises(RuntimeError):
            _ = s.editor

    def test_checkpoint_adds_to_undo(self):
        s = Session()
        s.new_project()
        before = len(s._undo_stack)
        s.checkpoint()
        assert len(s._undo_stack) == before + 1

    def test_undo_stack_limit_50(self):
        s = Session()
        s.new_project()
        for i in range(60):
            s.checkpoint()
        assert len(s._undo_stack) <= 50

    def test_is_modified_after_checkpoint(self):
        s = Session()
        s.new_project()
        assert not s.is_modified
        s.checkpoint()
        assert s.is_modified

    def test_open_invalid_json_raises(self, tmp_path):
        path = tmp_path / "bad.openscreen"
        path.write_text("not json at all")
        s = Session()
        with pytest.raises((RuntimeError, ValueError, Exception)):
            s.open_project(str(path))
