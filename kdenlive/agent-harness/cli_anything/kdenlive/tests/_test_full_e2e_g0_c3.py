# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowE2EMixin3:
    def test_split_then_filter_workflow(self):
        proj = create_project()
        import_clip(proj, "/vid.mp4", name="V", duration=20.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=20.0)
        split_clip(proj, 0, 0, split_at=10.0)
        add_filter(proj, 0, 1, "fade_out_video", {"duration": 2.0})
        filters = list_filters(proj, 0, 1)
        assert len(filters) == 1
        assert filters[0]["name"] == "fade_out_video"
    def test_session_with_full_workflow(self):
        sess = Session()
        proj = create_project(name="SessionWorkflow")
        sess.set_project(proj)

        sess.snapshot("import clips")
        import_clip(proj, "/a.mp4", name="A", duration=30.0)
        import_clip(proj, "/b.mp4", name="B", duration=30.0)

        sess.snapshot("add tracks")
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")

        sess.snapshot("place clips")
        add_clip_to_track(proj, 0, "clip0", out_point=15.0)

        history = sess.list_history()
        assert len(history) == 3

        sess.undo()
        assert len(sess.get_project()["tracks"][0]["clips"]) == 0

        sess.undo()
        assert len(sess.get_project()["tracks"]) == 0

        sess.redo()
        assert len(sess.get_project()["tracks"]) == 2
        sess.redo()
        assert len(sess.get_project()["tracks"][0]["clips"]) == 1
