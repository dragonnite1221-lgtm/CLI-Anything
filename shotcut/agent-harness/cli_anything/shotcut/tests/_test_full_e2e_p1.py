# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, session_with_tracks, video  # noqa: F401,E501


class TestProjectRoundtrip:
    def test_save_open_roundtrip(self, session, video):
        tl_mod.add_track(session, "video", "Main")
        tl_mod.add_track(session, "audio", "BGM")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1,
                        in_point="00:00:00.000", out_point="00:00:03.000",
                        caption="Intro Shot")
        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0,
                            params={"level": "1.4"})

        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(session, path)
            assert not session.is_modified

            s2 = Session()
            result = proj_mod.open_project(s2, path)
            assert result["track_count"] >= 3
            assert result["media_clip_count"] >= 1

            info = proj_mod.project_info(s2)
            assert any(os.path.basename(video) in c["resource"] for c in info["media_clips"])

            producers = get_all_producers(s2.root)
            found = False
            for p in producers:
                for f in p.findall("filter"):
                    if get_property(f, "mlt_service") == "brightness":
                        assert get_property(f, "level") == "1.4"
                        found = True
            assert found
        finally:
            os.unlink(path)

    def test_save_overwrite(self, session):
        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        try:
            proj_mod.save_project(session, path)
            tl_mod.add_track(session, "video")
            proj_mod.save_project(session, path)

            s2 = Session()
            proj_mod.open_project(s2, path)
            tracks = tl_mod.list_tracks(s2)
            assert len(tracks) >= 2
        finally:
            os.unlink(path)

    def test_project_info_with_content(self, session_with_tracks, video):
        s = session_with_tracks
        clip_id = media_mod.import_media(s, video)["clip_id"]
        tl_mod.add_clip(s, clip_id, 1, "00:00:00.000", "00:00:02.000")
        tl_mod.add_clip(s, clip_id, 1, "00:00:02.000", "00:00:04.000")
        tl_mod.add_clip(s, clip_id, 2, "00:00:00.000", "00:00:03.000")

        info = proj_mod.project_info(s)
        assert info["modified"] is True
        assert len(info["tracks"]) >= 4
        assert len(info["media_clips"]) == 1
