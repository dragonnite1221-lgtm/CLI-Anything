# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_new_session(self):
        s = Session()
        assert s.is_open is False
        assert s.is_modified is False

    def test_new_project(self):
        s = Session()
        s.new_project(850, 1100)
        assert s.is_open is True
        assert s.is_modified is False

    def test_undo_redo(self):
        s = Session()
        s.new_project()
        assert s.undo() is False  # Nothing to undo

        s.checkpoint()
        drawio_xml.add_vertex(s.root, "rectangle", 0, 0, 100, 50, "Test")
        assert len(drawio_xml.get_vertices(s.root)) == 1

        assert s.undo() is True
        assert len(drawio_xml.get_vertices(s.root)) == 0

        assert s.redo() is True
        assert len(drawio_xml.get_vertices(s.root)) == 1

    def test_multiple_undo(self):
        s = Session()
        s.new_project()

        s.checkpoint()
        drawio_xml.add_vertex(s.root, "rectangle", 0, 0, 100, 50, "First")

        s.checkpoint()
        drawio_xml.add_vertex(s.root, "rectangle", 200, 0, 100, 50, "Second")

        assert len(drawio_xml.get_vertices(s.root)) == 2
        s.undo()
        assert len(drawio_xml.get_vertices(s.root)) == 1
        s.undo()
        assert len(drawio_xml.get_vertices(s.root)) == 0

    def test_save_and_open(self):
        s = Session()
        s.new_project()
        drawio_xml.add_vertex(s.root, "rectangle", 0, 0, 100, 50, "Persisted")

        with tempfile.NamedTemporaryFile(suffix=".drawio", delete=False) as f:
            path = f.name

        try:
            s.save_project(path)
            assert not s.is_modified
            assert os.path.exists(path)

            s2 = Session()
            s2.open_project(path)
            assert s2.is_open
            cells = drawio_xml.get_vertices(s2.root)
            assert len(cells) == 1
            assert cells[0].get("value") == "Persisted"
        finally:
            os.unlink(path)

    def test_save_no_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project is open"):
            s.save_project("test.drawio")

    def test_open_nonexistent(self):
        s = Session()
        with pytest.raises(FileNotFoundError):
            s.open_project("/nonexistent/path.drawio")

    def test_status(self):
        s = Session()
        status = s.status()
        assert status["project_open"] is False

        s.new_project()
        drawio_xml.add_vertex(s.root, "rectangle", 0, 0, 100, 50)
        status = s.status()
        assert status["project_open"] is True
        assert status["shape_count"] == 1
        assert status["edge_count"] == 0
