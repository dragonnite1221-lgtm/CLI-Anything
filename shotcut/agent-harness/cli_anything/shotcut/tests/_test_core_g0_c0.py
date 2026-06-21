# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestSessionMixin0:
    def test_new_session(self):
        s = Session("test_session_1")
        assert s.session_id == "test_session_1"
        assert not s.is_open
        assert not s.is_modified
    def test_new_project(self):
        s = Session()
        s.new_project()
        assert s.is_open
        assert not s.is_modified
    def test_save_and_open(self, tmp_path):
        s = Session()
        s.new_project()
        path = str(tmp_path / "test.mlt")
        s.save_project(path)
        assert not s.is_modified
        s2 = Session()
        s2.open_project(path)
        assert s2.is_open
        assert s2.project_path == path
    def test_undo_redo(self):
        s = Session()
        s.new_project()
        assert not s.undo()
        s.checkpoint()
        from cli_anything.shotcut.utils.mlt_xml import add_track_to_tractor
        add_track_to_tractor(s.root, s.get_main_tractor(), "video")
        assert s.is_modified
        tracks_before = len(get_tractor_tracks(s.get_main_tractor()))
        assert s.undo()
        assert len(get_tractor_tracks(s.get_main_tractor())) < tracks_before
        assert s.redo()
        assert len(get_tractor_tracks(s.get_main_tractor())) == tracks_before
    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            Session().open_project("/nonexistent/path.mlt")
    def test_save_without_project(self):
        with pytest.raises(RuntimeError):
            Session().save_project("/tmp/test.mlt")
    def test_status(self):
        s = Session()
        assert s.status()["project_open"] is False
        s.new_project()
        status = s.status()
        assert status["project_open"] is True
        assert "profile" in status
    def test_resolve_refs_clips_on_open(self, tmp_path, dummy_file):
        s = Session()
        s.new_project()
        tl_mod.add_track(s, "video")
        clip_id = media_mod.import_media(s, dummy_file)["clip_id"]
        tl_mod.add_clip(s, clip_id, 1, "00:00:00.000", "00:00:05.000")
        path = str(tmp_path / "resolve.mlt")
        s.save_project(path)

        s2 = Session()
        s2.open_project(path)
        assert len(media_mod.list_media(s2)) == 1
        assert "clip0" in s2._bin_chains
        assert s2._clip_id_counter == 1
    def test_import_undo_import_redo_no_conflict(self, session_with_track, dummy_file, tmp_path):
        s = session_with_track
        r1 = media_mod.import_media(s, dummy_file)
        clip_id_a = r1["clip_id"]
        tl_mod.add_clip(s, clip_id_a, 1, "00:00:00.000", "00:00:05.000")

        f2 = str(tmp_path / "b.mp4")
        Path(f2).write_bytes(b"dummy2")
        r2 = media_mod.import_media(s, f2)
        clip_id_b = r2["clip_id"]
        assert clip_id_a != clip_id_b
        assert len(media_mod.list_media(s)) == 2

        s.undo()  # undo import B
        assert len(media_mod.list_media(s)) == 1
        assert clip_id_a in s._bin_chains
        assert clip_id_b not in s._bin_chains

        f3 = str(tmp_path / "c.mp4")
        Path(f3).write_bytes(b"dummy3")
        r3 = media_mod.import_media(s, f3)
        clip_id_c = r3["clip_id"]
        assert clip_id_c in s._bin_chains
        assert len(media_mod.list_media(s)) == 2

        # redo stack cleared by new import, undo all the way back
        assert s.undo()  # undo import C
        assert s.undo()  # undo add_clip A
        assert s.undo()  # undo import A
        assert len(media_mod.list_media(s)) == 0

        # redo path: import A → add_clip A → import C (B is lost)
        s.redo()
        assert clip_id_a in s._bin_chains
        s.redo()
        s.redo()
        assert clip_id_c in s._bin_chains
        assert len(media_mod.list_media(s)) == 2
    def test_resolve_refs_tracks_on_open(self, tmp_path):
        s = Session()
        s.new_project()
        tl_mod.add_track(s, "video", "V1")
        tl_mod.add_track(s, "audio", "A1")
        path = str(tmp_path / "tracks.mlt")
        s.save_project(path)

        s2 = Session()
        s2.open_project(path)
        assert len(tl_mod.list_tracks(s2)) == 3
