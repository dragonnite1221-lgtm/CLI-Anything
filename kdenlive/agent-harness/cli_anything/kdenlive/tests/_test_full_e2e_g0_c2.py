# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestWorkflowE2EMixin2:
    def test_complex_timeline_xml(self):
        proj = create_project(name="Complex", profile="hd1080p30")
        for i in range(5):
            import_clip(proj, f"/clip{i}.mp4", name=f"Clip{i}", duration=30.0)
        add_track(proj, track_type="video")
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")

        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=15.0)
        add_clip_to_track(proj, 0, "clip1", position=15.0, out_point=15.0)
        add_clip_to_track(proj, 1, "clip2", position=5.0, out_point=20.0)
        add_clip_to_track(proj, 2, "clip3", position=0.0, out_point=30.0)

        add_filter(proj, 0, 0, "brightness", {"level": 1.1})
        add_filter(proj, 0, 0, "blur", {"hblur": 3, "vblur": 3})
        add_filter(proj, 0, 1, "fade_in_video", {"duration": 0.5})

        add_transition(proj, "dissolve", 0, 1, position=5.0, duration=3.0)

        add_guide(proj, 0.0, label="Start")
        add_guide(proj, 15.0, label="Mid")
        add_guide(proj, 30.0, label="End")

        root = ET.fromstring(generate_kdenlive_xml(proj))

        # 5 bin clips → bin chains for each + per-track chains for used clips
        main_bin = root.find(".//playlist[@id='main_bin']")
        bin_entries = [e for e in main_bin.findall("entry") if not e.get("producer", "").startswith("{")]
        assert len(bin_entries) == 5

        # 3 tracks × 2 playlists + main_bin = 7
        playlists = root.findall("playlist")
        assert len(playlists) == 7

        # 3 user filters on clips
        user_filters = root.findall(".//entry/filter")
        assert len(user_filters) == 3

        # 1 user transition (luma/dissolve)
        seq = _find_sequence(root)
        luma_trans = [t for t in seq.findall("transition") if t.get("mlt_service") == "luma"]
        assert len(luma_trans) == 1

        # Guides in sequence tractor
        guides_prop = seq.find("property[@name='kdenlive:sequenceproperties.guides']")
        assert guides_prop is not None
        data = json.loads(guides_prop.text)
        assert len(data) == 3
    def test_move_clip_then_export(self):
        proj = create_project()
        import_clip(proj, "/vid.mp4", name="V", duration=30.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=10.0)
        move_clip(proj, 0, 0, new_position=5.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        blanks = root.findall(".//blank")
        assert len(blanks) > 0
    def test_project_info_after_edits(self):
        proj = create_project(name="InfoTest")
        import_clip(proj, "/a.mp4", name="A", duration=10.0)
        import_clip(proj, "/b.mp4", name="B", duration=20.0)
        add_track(proj, track_type="video")
        add_track(proj, track_type="audio")
        add_clip_to_track(proj, 0, "clip0", out_point=10.0)
        add_guide(proj, 5.0, label="X")

        info = get_project_info(proj)
        assert info["counts"]["bin_clips"] == 2
        assert info["counts"]["tracks"] == 2
        assert info["counts"]["clips_on_timeline"] == 1
        assert info["counts"]["guides"] == 1
    def test_all_filter_types_in_xml(self):
        proj = create_project()
        import_clip(proj, "/vid.mp4", name="V", duration=30.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=30.0)

        for fname in FILTER_REGISTRY:
            add_filter(proj, 0, 0, fname)

        root = ET.fromstring(generate_kdenlive_xml(proj))
        user_filters = root.findall(".//entry/filter")
        assert len(user_filters) == len(FILTER_REGISTRY)
    def test_xml_write_to_file(self):
        proj = create_project(name="FileTest")
        import_clip(proj, "/v.mp4", name="V", duration=10.0)
        add_track(proj)
        add_clip_to_track(proj, 0, "clip0", out_point=10.0)

        xml = generate_kdenlive_xml(proj)
        with tempfile.NamedTemporaryFile(suffix=".kdenlive", delete=False, mode="w") as f:
            f.write(xml)
            path = f.name
        try:
            with open(path, "r") as f:
                content = f.read()
            assert content.startswith('<?xml version="1.0"')
            assert "</mlt>" in content
        finally:
            os.unlink(path)
    def test_timecode_in_workflow(self):
        tc = "00:01:30.000"
        secs = timecode_to_seconds(tc)
        assert secs == 90.0

        frames = seconds_to_frames(secs, 30, 1)
        assert frames == 2700

        back_tc = seconds_to_timecode(secs)
        assert back_tc == "00:01:30.000"
