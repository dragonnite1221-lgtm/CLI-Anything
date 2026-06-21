# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestSessionUndoRedo:
    """Test session undo/redo in realistic workflows."""

    def test_undo_add_source(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)

        sess.snapshot("add camera")
        add_source(proj, "video_capture", name="Camera")
        assert len(proj["scenes"][0]["sources"]) == 1

        sess.undo()
        assert len(sess.get_project()["scenes"][0]["sources"]) == 0

        sess.redo()
        assert len(sess.get_project()["scenes"][0]["sources"]) == 1

    def test_undo_add_scene(self):
        sess = Session()
        proj = create_project()
        sess.set_project(proj)

        sess.snapshot("add scene")
        add_scene(proj, name="BRB")
        assert len(proj["scenes"]) == 2

        sess.undo()
        assert len(sess.get_project()["scenes"]) == 1

    def test_undo_filter_chain(self):
        sess = Session()
        proj = create_project()
        add_source(proj, "video_capture", name="Camera")
        sess.set_project(proj)

        sess.snapshot("add filter")
        add_filter(proj, "chroma_key", 0)
        assert len(proj["scenes"][0]["sources"][0]["filters"]) == 1

        sess.snapshot("add filter 2")
        add_filter(proj, "color_correction", 0)
        assert len(proj["scenes"][0]["sources"][0]["filters"]) == 2

        sess.undo()
        assert len(sess.get_project()["scenes"][0]["sources"][0]["filters"]) == 1

        sess.undo()
        assert len(sess.get_project()["scenes"][0]["sources"][0]["filters"]) == 0

    def test_undo_audio_changes(self):
        sess = Session()
        proj = create_project()
        add_audio_source(proj, name="Mic", volume=1.0)
        sess.set_project(proj)

        sess.snapshot("change volume")
        set_volume(proj, 0, 0.5)
        assert proj["audio_sources"][0]["volume"] == 0.5

        sess.undo()
        assert sess.get_project()["audio_sources"][0]["volume"] == 1.0

    def test_multiple_undo_redo(self):
        sess = Session()
        proj = create_project(name="v1")
        sess.set_project(proj)

        sess.snapshot("rename to v2")
        proj["name"] = "v2"

        sess.snapshot("rename to v3")
        proj["name"] = "v3"

        sess.snapshot("rename to v4")
        proj["name"] = "v4"

        sess.undo()
        assert sess.get_project()["name"] == "v3"
        sess.undo()
        assert sess.get_project()["name"] == "v2"
        sess.undo()
        assert sess.get_project()["name"] == "v1"

        sess.redo()
        assert sess.get_project()["name"] == "v2"
        sess.redo()
        assert sess.get_project()["name"] == "v3"
