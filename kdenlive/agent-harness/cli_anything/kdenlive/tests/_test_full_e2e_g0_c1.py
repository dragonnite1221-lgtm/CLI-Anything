# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowE2EMixin1:
    def test_undo_redo_workflow(self):
        sess = Session()
        proj = create_project(name="UndoTest")
        sess.set_project(proj)

        sess.snapshot("import clip")
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        assert len(proj["bin"]) == 1

        sess.snapshot("add track")
        add_track(proj)
        assert len(proj["tracks"]) == 1

        sess.undo()
        assert len(sess.get_project()["tracks"]) == 0

        sess.undo()
        assert len(sess.get_project()["bin"]) == 0

        sess.redo()
        assert len(sess.get_project()["bin"]) == 1

        sess.redo()
        assert len(sess.get_project()["tracks"]) == 1
    def test_save_load_roundtrip(self):
        proj = create_project(name="Roundtrip", profile="hd1080p25")
        import_clip(proj, "/vid.mp4", name="Video", duration=60.0)
        import_clip(proj, "/aud.wav", name="Audio", duration=60.0, clip_type="audio")
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")
        add_clip_to_track(proj, 0, "clip0", out_point=30.0)
        add_clip_to_track(proj, 1, "clip1", out_point=30.0)
        add_filter(proj, 0, 0, "brightness", {"level": 1.2})
        add_transition(proj, "dissolve", 0, 1, position=5.0, duration=2.0)
        add_guide(proj, 10.0, label="Mark")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_project(proj, path)
            loaded = open_project(path)

            assert loaded["name"] == "Roundtrip"
            assert loaded["profile"]["fps_num"] == 25
            assert len(loaded["bin"]) == 2
            assert len(loaded["tracks"]) == 2
            assert len(loaded["tracks"][0]["clips"]) == 1
            assert len(loaded["tracks"][0]["clips"][0]["filters"]) == 1
            assert len(loaded["transitions"]) == 1
            assert len(loaded["guides"]) == 1

            xml = generate_kdenlive_xml(loaded)
            root = ET.fromstring(xml)
            assert root.tag == "mlt"
        finally:
            os.unlink(path)
    def test_render_presets_available(self):
        presets = list_render_presets()
        assert len(presets) == len(RENDER_PRESETS)
        names = [p["name"] for p in presets]
        assert "h264_hq" in names
        assert "h264_fast" in names
        assert "prores" in names
    def test_all_profiles_produce_valid_xml(self):
        from cli_anything.kdenlive.core.project import PROFILES
        for name in PROFILES:
            proj = create_project(profile=name)
            root = ET.fromstring(generate_kdenlive_xml(proj))
            assert root.tag == "mlt"
            assert root.find("profile") is not None
