# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestMedia:
    def test_probe_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            media_mod.probe_media("/nonexistent/file.mp4")

    def test_probe_basic(self, dummy_file):
        result = media_mod.probe_media(dummy_file)
        assert result["filename"] == os.path.basename(dummy_file)
        assert result["size_bytes"] > 0

    def test_probe_basic_video_type(self, dummy_file):
        result = media_mod.probe_media(dummy_file)
        assert result["media_type"] == "video"

    def test_probe_basic_audio_type(self, tmp_path):
        p = tmp_path / "audio.mp3"
        p.write_bytes(b"dummy")
        result = media_mod.probe_media(str(p))
        assert result["media_type"] == "audio"

    def test_probe_basic_image_type(self, tmp_path, monkeypatch):
        monkeypatch.setattr(media_mod, "_find_tool", lambda name: None)
        p = tmp_path / "image.png"
        p.write_bytes(b"dummy")
        result = media_mod.probe_media(str(p))
        assert result["media_type"] == "image"

    def test_parse_fps_fraction(self):
        assert media_mod._parse_fps("30000/1001") == 29.97

    def test_parse_fps_integer(self):
        assert media_mod._parse_fps("30") == 30.0

    def test_parse_fps_zero_denominator(self):
        assert media_mod._parse_fps("30/0") == 0.0

    def test_parse_fps_invalid(self):
        assert media_mod._parse_fps("abc") == 0.0

    def test_list_media_empty(self, session):
        assert media_mod.list_media(session) == []

    def test_list_media_with_clip(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")
        result = media_mod.list_media(session_with_track)
        assert len(result) >= 1
        assert any(dummy_file in m["resource"] for m in result)

    def test_list_media_no_double_count(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")
        assert len(media_mod.list_media(session_with_track)) == 1

    def test_import_media_returns_clip_id(self, session_with_track, dummy_file):
        result = media_mod.import_media(session_with_track, dummy_file)
        assert result["clip_id"] == "clip0"
        assert result["source"] == os.path.abspath(dummy_file)

    def test_import_media_idempotent(self, session_with_track, dummy_file):
        r1 = media_mod.import_media(session_with_track, dummy_file)
        r2 = media_mod.import_media(session_with_track, dummy_file)
        assert r1["clip_id"] == r2["clip_id"]
        assert r2["already_imported"] is True

    def test_import_media_no_project(self, dummy_file):
        s = Session()
        with pytest.raises(RuntimeError, match="No project"):
            media_mod.import_media(s, dummy_file)

    def test_import_media_file_not_found(self, session_with_track):
        with pytest.raises(FileNotFoundError):
            media_mod.import_media(session_with_track, "/nonexistent.mp4")

    def test_import_media_sets_modified(self, session, dummy_file):
        tl_mod.add_track(session, "video")
        assert session.is_modified is True
        session.undo()
        assert session.is_modified is False
        media_mod.import_media(session, dummy_file)
        assert session.is_modified is True

    def test_import_media_undo(self, session_with_track, dummy_file):
        media_mod.import_media(session_with_track, dummy_file)
        assert len(media_mod.list_media(session_with_track)) == 1
        session_with_track.undo()
        assert len(media_mod.list_media(session_with_track)) == 0

    def test_get_clip_info(self, session_with_track, dummy_file):
        result = media_mod.import_media(session_with_track, dummy_file)
        info = media_mod.get_clip_info(session_with_track, result["clip_id"])
        assert info["clip_id"] == "clip0"
        assert dummy_file in info["resource"]

    def test_get_clip_info_not_found(self, session_with_track):
        with pytest.raises(ValueError, match="not found"):
            media_mod.get_clip_info(session_with_track, "clip999")

    def test_check_media_files_present(self, session_with_track, dummy_file):
        media_mod.import_media(session_with_track, dummy_file)
        result = media_mod.check_media_files(session_with_track)
        assert result["total"] == 1
        assert result["all_present"] is True

    def test_check_media_files_empty(self, session):
        result = media_mod.check_media_files(session)
        assert result["total"] == 0
        assert result["all_present"] is True

    def test_check_media_files_missing(self, session_with_track, tmp_path):
        f = tmp_path / "temp_video.mp4"
        f.write_bytes(b"dummy")
        media_mod.import_media(session_with_track, str(f))
        os.unlink(str(f))
        result = media_mod.check_media_files(session_with_track)
        assert result["all_present"] is False
        assert len(result["missing"]) == 1

    def test_probe_basic_mlt_type(self, tmp_path, monkeypatch):
        monkeypatch.setattr(media_mod, "_find_tool", lambda name: None)
        p = tmp_path / "project.mlt"
        p.write_bytes(b"<mlt></mlt>")
        result = media_mod.probe_media(str(p))
        assert result["media_type"] == "mlt_project"

    def test_import_media_with_caption(self, session_with_track, dummy_file):
        result = media_mod.import_media(session_with_track, dummy_file, caption="My Clip")
        assert result["caption"] == "My Clip"
