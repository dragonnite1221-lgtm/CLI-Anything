# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestSession:
    def test_create_session(self):
        s = Session()
        assert not s.has_project()
        assert s.project_data is None

    def test_set_project(self):
        s = Session()
        s.set_project({"name": "test"}, "/tmp/test.mscz")
        assert s.has_project()
        assert s.project_data["name"] == "test"
        assert s.project_path == "/tmp/test.mscz"

    def test_get_project_raises_without_open(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project"):
            s.get_project()

    def test_undo_redo(self):
        s = Session()
        s.set_project({"name": "v1"})
        s.snapshot("edit 1")
        s.project_data["name"] = "v2"
        s.snapshot("edit 2")
        s.project_data["name"] = "v3"

        # Undo edit 2
        desc = s.undo()
        assert desc == "edit 2"
        assert s.project_data["name"] == "v2"

        # Undo edit 1
        desc = s.undo()
        assert desc == "edit 1"
        assert s.project_data["name"] == "v1"

        # Redo edit 1
        desc = s.redo()
        assert desc == "edit 1"
        assert s.project_data["name"] == "v2"

    def test_undo_empty_raises(self):
        s = Session()
        s.set_project({"name": "test"})
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            s.undo()

    def test_redo_empty_raises(self):
        s = Session()
        s.set_project({"name": "test"})
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            s.redo()

    def test_snapshot_clears_redo(self):
        s = Session()
        s.set_project({"name": "v1"})
        s.snapshot("edit 1")
        s.project_data["name"] = "v2"
        s.undo()
        # New edit should clear redo stack
        s.snapshot("edit 2")
        assert len(s.redo_stack) == 0

    def test_history(self):
        s = Session()
        s.set_project({"name": "test"})
        s.snapshot("action 1")
        s.snapshot("action 2")
        s.snapshot("action 3")
        assert s.list_history() == ["action 1", "action 2", "action 3"]

    def test_status(self):
        s = Session()
        s.set_project({"name": "test"}, "/tmp/test.mscz")
        s.snapshot("edit")
        status = s.status()
        assert status["project_path"] == "/tmp/test.mscz"
        assert status["undo_depth"] == 1
        assert status["redo_depth"] == 0

    def test_modified_flag(self):
        s = Session()
        s.set_project({"name": "test"})
        assert not s.is_modified()
        s.snapshot("edit")
        assert s.is_modified()

    def test_save_session(self):
        s = Session()
        s.set_project({"name": "test"}, "/tmp/test.mscz")
        s.snapshot("edit")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.mscz")
            result = s.save_session(path)
            assert os.path.isfile(result)
            with open(result) as f:
                data = json.load(f)
            assert data["history"] == ["edit"]
