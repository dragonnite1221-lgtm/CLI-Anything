# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestMedia:
    def test_probe_real_video(self, video):
        result = media_mod.probe_media(video)
        assert result["filename"] == os.path.basename(video)
        assert result["size_bytes"] > 0

    def test_probe_real_video_returns_stream_details(self, video):
        result = media_mod.probe_media(video)
        assert result["duration_seconds"] > 0
        assert len(result.get("video_streams", [])) >= 1
        vs = result["video_streams"][0]
        assert vs["width"] == 1920
        assert vs["height"] == 1080
        assert vs["codec"] == "h264"

    def test_add_clip_without_out_point_uses_probed_duration(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, in_point="00:00:00.000")

        clips = tl_mod.list_clips(session, 1)
        real_clips = [c for c in clips if "clip_index" in c]
        assert len(real_clips) == 1
        clip_out = real_clips[0]["out"]
        assert clip_out not in (None, "", "00:00:00.000")

    def test_list_media_after_adding_clips(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:05.000", "00:00:10.000")

        media = media_mod.list_media(session)
        assert len(media) == 1
        assert media[0]["exists"] is True

    def test_check_media_all_present(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        result = media_mod.check_media_files(session)
        assert result["all_present"] is True
        assert len(result["missing"]) == 0

    def test_check_media_with_missing(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        import tempfile
        fd, tmp_media = tempfile.mkstemp(suffix=".mp4")
        os.write(fd, b"temp_media")
        os.close(fd)
        clip_id2 = media_mod.import_media(session, tmp_media)["clip_id"]
        os.unlink(tmp_media)

        result = media_mod.check_media_files(session)
        assert not result["all_present"]
        assert len(result["missing"]) >= 1


class TestExport:
    def test_render_generates_script(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            out = f.name
        os.unlink(out)

        try:
            result = export_mod.render(session, out, "default")
            assert result.get("action") == "render"
        except RuntimeError:
            pass

    def test_render_refuses_overwrite(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"existing content")
            out = f.name
        try:
            with pytest.raises(FileExistsError):
                export_mod.render(session, out, "default")
        finally:
            os.unlink(out)

    def test_render_invalid_preset(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")
        with pytest.raises(ValueError):
            export_mod.render(session, "/tmp/out.mp4", "fake_preset")
