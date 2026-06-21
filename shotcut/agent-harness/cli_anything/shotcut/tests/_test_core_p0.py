# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestTimecode:
    def test_plain_frame_number(self):
        assert timecode_to_frames("100") == 100

    def test_hh_mm_ss_mmm(self):
        frames = timecode_to_frames("00:00:01.000")
        assert 29 <= frames <= 30

    def test_hh_mm_ss(self):
        frames = timecode_to_frames("00:01:00")
        fps = 30000 / 1001
        expected = int(60 * fps)
        assert abs(frames - expected) <= 1

    def test_seconds_decimal(self):
        frames = timecode_to_frames("2.5")
        fps = 30000 / 1001
        expected = int(2.5 * fps)
        assert abs(frames - expected) <= 1

    def test_roundtrip(self):
        for original_frames in [0, 1, 30, 900, 1800, 54000]:
            tc = frames_to_timecode(original_frames)
            back = timecode_to_frames(tc)
            assert abs(back - original_frames) <= 1, \
                f"Roundtrip failed: {original_frames} -> {tc} -> {back}"

    def test_invalid_timecode(self):
        with pytest.raises(ValueError):
            timecode_to_frames("invalid")

    def test_negative_frames(self):
        assert frames_to_timecode(-5) == "00:00:00.000"

    def test_frames_to_seconds(self):
        secs = frames_to_seconds(30, 30000, 1001)
        assert abs(secs - 1.001) < 0.01

    def test_seconds_to_frames(self):
        frames = seconds_to_frames(1.0, 30000, 1001)
        assert 29 <= frames <= 30


class TestMltXml:
    def test_create_blank_project(self):
        root = create_blank_project(PROFILE_HD1080)
        assert root.tag == "mlt"
        assert "Shotcut" in (root.get("title") or "")
        prof = root.find("profile")
        assert prof is not None
        assert prof.get("width") == "1920"
        assert get_main_tractor(root) is not None

    def test_main_tractor_structure(self):
        root = create_blank_project(PROFILE_HD1080)
        tractor = get_main_tractor(root)
        assert tractor.find("multitrack") is None
        tracks = tractor.findall("track")
        assert len(tracks) == 1
        assert tracks[0].get("producer") == "background"
        assert "Shotcut" in tractor.get("title")

    def test_write_and_parse(self, tmp_path):
        root = create_blank_project(PROFILE_HD1080)
        tmpfile = str(tmp_path / "test.mlt")
        write_mlt(root, tmpfile)
        parsed = parse_mlt(tmpfile)
        assert parsed.tag == "mlt"
        assert parsed.find("profile").get("width") == "1920"

    def test_write_mlt_normalizes_late_media_nodes(self, tmp_path):
        root = create_blank_project(PROFILE_HD1080)
        late_chain = ET.Element("chain")
        late_chain.set("id", "late_chain")
        late_chain.set("in", "00:00:00.000")
        late_chain.set("out", "00:00:01.000")
        set_property(late_chain, "resource", "/tmp/fake.mp4")
        set_property(late_chain, "mlt_service", "avformat-novalidate")
        root.append(late_chain)

        tmpfile = str(tmp_path / "ordered.mlt")
        write_mlt(root, tmpfile)
        parsed = parse_mlt(tmpfile)
        children = list(parsed)
        first_playlist_or_tractor = min(
            idx for idx, child in enumerate(children) if child.tag in ("playlist", "tractor")
        )
        late_idx = next(
            idx
            for idx, child in enumerate(children)
            if child.tag == "chain" and child.get("id") == "late_chain"
        )
        assert late_idx < first_playlist_or_tractor

    def test_properties(self):
        import xml.etree.ElementTree as ET
        elem = ET.Element("producer")
        set_property(elem, "resource", "/test/video.mp4")
        assert get_property(elem, "resource") == "/test/video.mp4"
        assert get_property(elem, "nonexistent") is None
        assert get_property(elem, "nonexistent", "default") == "default"

    def test_mlt_to_string(self):
        root = create_blank_project(PROFILE_HD1080)
        xml_str = mlt_to_string(root)
        assert "<?xml" in xml_str
        assert "<mlt" in xml_str
