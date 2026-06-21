# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestIntegration:
    def test_full_workflow(self, dummy_file, tmp_path):
        s = Session()
        proj_mod.new_project(s, "hd1080p30")
        tl_mod.add_track(s, "video", "V1")
        tl_mod.add_track(s, "audio", "A1")
        clip_id = media_mod.import_media(s, dummy_file)["clip_id"]
        tl_mod.add_clip(s, clip_id, 1, "00:00:00.000", "00:00:05.000", caption="Intro")
        tl_mod.add_clip(s, clip_id, 1, "00:00:00.000", "00:00:10.000", caption="Main")
        filt_mod.add_filter(s, "brightness", track_index=1, clip_index=0, params={"level": "1.2"})
        tl_mod.trim_clip(s, 1, 1, in_point="00:00:02.000")
        path = str(tmp_path / "project.mlt")
        proj_mod.save_project(s, path)
        s2 = Session()
        proj_mod.open_project(s2, path)
        assert proj_mod.project_info(s2)["media_clips"][0]["resource"] == dummy_file
        tl_mod.add_track(s, "video", "V2")
        s.undo()

    def test_save_load_roundtrip_preserves_filters(self, dummy_file, tmp_path):
        s = Session()
        proj_mod.new_project(s)
        tl_mod.add_track(s, "video")
        clip_id = media_mod.import_media(s, dummy_file)["clip_id"]
        tl_mod.add_clip(s, clip_id, 1, "00:00:00.000", "00:00:05.000")
        filt_mod.add_filter(s, "brightness", track_index=1, clip_index=0, params={"level": "0.8"})
        path = str(tmp_path / "project.mlt")
        proj_mod.save_project(s, path)
        s2 = Session()
        proj_mod.open_project(s2, path)
        found = False
        for prod in get_all_producers(s2.root):
            for filt in prod.findall("filter"):
                if get_property(filt, "mlt_service") == "brightness":
                    assert get_property(filt, "level") == "0.8"
                    found = True
        assert found
