# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestProject:
    def test_new_project(self):
        s = Session()
        result = proj_mod.new_project(s, "hd1080p30")
        assert result["profile"] == "hd1080p30"

    def test_new_project_invalid_profile(self):
        with pytest.raises(ValueError):
            proj_mod.new_project(Session(), "invalid_profile")

    def test_project_info(self, session):
        info = proj_mod.project_info(session)
        assert "profile" in info
        assert "tracks" in info
        assert "media_clips" in info

    def test_list_profiles(self):
        profiles = proj_mod.list_profiles()
        assert "hd1080p30" in profiles
        assert "4k30" in profiles

    def test_save_project(self, session, tmp_path):
        path = str(tmp_path / "test.mlt")
        result = proj_mod.save_project(session, path)
        assert result["path"] == path
        assert os.path.isfile(path)

    def test_open_and_info(self, session, tmp_path):
        path = str(tmp_path / "test.mlt")
        proj_mod.save_project(session, path)
        s2 = Session()
        result = proj_mod.open_project(s2, path)
        assert result["path"] == path

    def test_project_info_no_double_count_chains(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")
        info = proj_mod.project_info(session_with_track)
        assert len(info["media_clips"]) == 1

    def test_project_info_clip_count_excludes_transitions(self, session_with_track, dummy_file):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:10.000")
        trans_mod.add_transition(session_with_track, "dissolve", track_index=1,
                                 clip_a_index=0, duration_frames=14)
        info = proj_mod.project_info(session_with_track)
        assert info["tracks"][1]["clip_count"] == 2
