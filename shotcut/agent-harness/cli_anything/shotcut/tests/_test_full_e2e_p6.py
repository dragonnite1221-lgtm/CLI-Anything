# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import session, video  # noqa: F401,E501


class TestRealWorldWorkflows:
    def test_youtube_video_edit(self, session, video):
        tl_mod.add_track(session, "video", "Main")
        tl_mod.add_track(session, "video", "B-Roll")
        tl_mod.add_track(session, "audio", "Music")
        tl_mod.add_track(session, "audio", "Voiceover")

        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:03.000",
                        caption="Intro")
        tl_mod.add_clip(session, clip_id, 1, "00:00:03.000", "00:00:08.000",
                        caption="Main Content")
        tl_mod.add_clip(session, clip_id, 1, "00:00:08.000", "00:00:10.000",
                        caption="Outro")

        tl_mod.add_clip(session, clip_id, 2, "00:00:01.000", "00:00:04.000",
                        caption="B-Roll Overlay")

        tl_mod.trim_clip(session, 1, 0, in_point="00:00:01.000")

        filt_mod.add_filter(session, "text", track_index=1, clip_index=0,
                            params={
                                "argument": "MY AWESOME VIDEO",
                                "size": "64",
                                "fgcolour": "#ffffffff",
                                "halign": "center",
                                "valign": "middle",
                            })

        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=1,
                            params={"level": "1.1"})
        filt_mod.add_filter(session, "fadein-video", track_index=1, clip_index=0)
        filt_mod.add_filter(session, "fadeout-video", track_index=1, clip_index=2)

        tl_mod.set_track_mute(session, 2, True)

        timeline = tl_mod.show_timeline(session)
        main_track = [t for t in timeline["tracks"] if t.get("name") == "Main"][0]
        assert len([c for c in main_track["clips"] if "clip_index" in c]) == 3

        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False) as f:
            path = f.name
        proj_mod.save_project(session, path)

        s2 = Session()
        proj_mod.open_project(s2, path)
        info = proj_mod.project_info(s2)
        assert len(info["tracks"]) >= 5
        os.unlink(path)

    def test_montage_sequence(self, session, video):
        tl_mod.add_track(session, "video", "Montage")

        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.split_clip(session, 1, 0, "00:00:02.000")
        tl_mod.split_clip(session, 1, 1, "00:00:04.000")
        tl_mod.split_clip(session, 1, 2, "00:00:06.000")
        tl_mod.split_clip(session, 1, 3, "00:00:08.000")

        clips = [c for c in tl_mod.list_clips(session, 1) if "clip_index" in c]
        assert len(clips) == 5

        effects = ["brightness", "sepia", "blur", "grayscale", "invert"]
        for i, eff in enumerate(effects):
            filt_mod.add_filter(session, eff, track_index=1, clip_index=i)

        for i in range(5):
            filters = filt_mod.list_filters(session, track_index=1, clip_index=i)
            assert len(filters) == 1

    def test_multicam_edit(self, session, video):
        tl_mod.add_track(session, "video", "Cam1")
        tl_mod.add_track(session, "video", "Cam2")
        tl_mod.add_track(session, "audio", "Mixed")

        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:05.000")
        tl_mod.add_clip(session, clip_id, 1, "00:00:05.000", "00:00:10.000")
        tl_mod.add_clip(session, clip_id, 2, "00:00:00.000", "00:00:05.000")
        tl_mod.add_clip(session, clip_id, 2, "00:00:05.000", "00:00:10.000")
        tl_mod.add_clip(session, clip_id, 3, "00:00:00.000", "00:00:10.000")

        tl_mod.set_track_hidden(session, 1, True)
        tl_mod.set_track_hidden(session, 1, False)

        filt_mod.add_filter(session, "volume", track_index=3,
                          params={"level": "0.8"})

        timeline = tl_mod.show_timeline(session)
        assert len(timeline["tracks"]) >= 4

    def test_color_grading_pipeline(self, session, video):
        tl_mod.add_track(session, "video", "V1")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")

        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0,
                            params={"level": "1.2"})
        filt_mod.add_filter(session, "saturation", track_index=1, clip_index=0,
                            params={"saturation": "0.8"})
        filt_mod.add_filter(session, "contrast", track_index=1, clip_index=0,
                            params={"level": "1.1"})

        filters = filt_mod.list_filters(session, track_index=1, clip_index=0)
        assert len(filters) == 3

        for i, f in enumerate(filters):
            filt_mod.set_filter_param(session, i, "disable", "1",
                                       track_index=1, clip_index=0)

        filters = filt_mod.list_filters(session, track_index=1, clip_index=0)
        for f in filters:
            assert f["params"].get("disable") == "1"

    def test_iterative_refinement(self, session, video):
        tl_mod.add_track(session, "video")
        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:10.000")

        filt_mod.add_filter(session, "brightness", track_index=1, clip_index=0,
                            params={"level": "2.0"})
        filt_mod.set_filter_param(session, 0, "level", "1.8",
                                   track_index=1, clip_index=0)
        filt_mod.set_filter_param(session, 0, "level", "1.5",
                                   track_index=1, clip_index=0)

        session.undo()
        filters = filt_mod.list_filters(session, 1, 0)
        assert filters[0]["params"]["level"] == "1.8"

        session.undo()
        filters = filt_mod.list_filters(session, 1, 0)
        assert filters[0]["params"]["level"] == "2.0"

    def test_full_timeline_visualization(self, session, video):
        tl_mod.add_track(session, "video", "V1")
        tl_mod.add_track(session, "audio", "A1")

        clip_id = media_mod.import_media(session, video)["clip_id"]
        tl_mod.add_clip(session, clip_id, 1, "00:00:00.000", "00:00:03.000", caption="Intro")
        tl_mod.add_clip(session, clip_id, 1, "00:00:03.000", "00:00:07.000", caption="Body")
        tl_mod.add_clip(session, clip_id, 1, "00:00:07.000", "00:00:10.000", caption="Outro")
        tl_mod.add_clip(session, clip_id, 2, "00:00:00.000", "00:00:10.000", caption="BGM")

        result = tl_mod.show_timeline(session)
        assert result["fps_num"] == 30000
        assert len(result["tracks"]) >= 3

        v1 = [t for t in result["tracks"] if t.get("name") == "V1"][0]
        assert len([c for c in v1["clips"] if "clip_index" in c]) == 3
