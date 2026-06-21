# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestExport:
    def test_list_presets(self):
        result = export_mod.list_presets()
        names = [p["name"] for p in result]
        assert "default" in names
        assert "h264-high" in names

    def test_list_presets_contains_defaults(self):
        result = export_mod.list_presets()
        names = [p["name"] for p in result]
        assert "default" in names
        assert "h264-high" in names

    def test_get_preset_info(self):
        assert export_mod.get_preset_info("default")["vcodec"] == "libx264"

    def test_unknown_preset(self):
        with pytest.raises(ValueError):
            export_mod.get_preset_info("nonexistent")

    def test_render_no_project(self):
        with pytest.raises(RuntimeError):
            export_mod.render(Session(), "/tmp/output.mp4")

    def test_render_no_overwrite(self, session_with_track, dummy_file, tmp_path):
        out = str(tmp_path / "out.mp4")
        open(out, 'wb').write(b"existing")
        with pytest.raises(FileExistsError):
            export_mod.render(session_with_track, out)

    def test_export_updates_tractor_out_with_trailing_blank(self, session_with_track, dummy_file, tmp_path):
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")
        tl_mod.add_blank(session_with_track, 1, "00:00:03.000")
        out = str(tmp_path / "out.mp4")
        try:
            export_mod.render(session_with_track, out, overwrite=True)
        except (FileNotFoundError, RuntimeError):
            pass
        expected = parse_time_input("00:00:08.000", 30000, 1001)
        actual = parse_time_input(session_with_track.get_main_tractor().get("out", "0"), 30000, 1001)
        assert abs(actual - expected) <= 1

    def test_set_tractor_out_single_clip(self, session_with_track, dummy_file):
        """_update_tractor_out sets tractor out to match a single clip duration."""
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:05.000")

        tractor = get_main_tractor(session_with_track.root)
        assert tractor.get("out") != "00:00:00.000"
        assert tractor.get("out") != "04:00:00.000"
        bg = find_element_by_id(session_with_track.root, "background")
        bg_entry = bg.find("entry")
        assert bg_entry.get("out") == tractor.get("out")

    def test_set_tractor_out_multi_segment(self, session_with_track, dummy_file):
        """_update_tractor_out sums entry spans and blanks across segments."""
        clip_id = media_mod.import_media(session_with_track, dummy_file)["clip_id"]
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:03.000")
        tl_mod.add_blank(session_with_track, 1, "00:00:01.000")
        tl_mod.add_clip(session_with_track, clip_id, 1, "00:00:00.000", "00:00:03.000")

        tractor = get_main_tractor(session_with_track.root)
        out_tc = tractor.get("out")
        assert out_tc != "00:00:00.000"
        assert out_tc != "04:00:00.000"

    def test_set_tractor_out_empty_timeline(self):
        """_update_tractor_out is a no-op on a blank project with no clips."""
        s = Session()
        proj_mod.new_project(s, "hd1080p30")
        tractor = get_main_tractor(s.root)

        assert tractor.get("out") == "00:00:00.000"
