# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestXMLGeneration:
    def _make_full_project(self):
        """Create a project with clips, tracks, filters, transitions, guides."""
        proj = create_project(name="TestProject", profile="hd1080p30")
        import_clip(proj, "/path/to/interview.mp4", name="Interview", duration=120.0)
        import_clip(proj, "/path/to/broll.mp4", name="BRoll", duration=60.0)
        import_clip(proj, "/path/to/music.mp3", name="Music", duration=180.0, clip_type="audio")

        add_track(proj, name="V1", track_type="video")
        add_track(proj, name="V2", track_type="video")
        add_track(proj, name="A1", track_type="audio")

        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=30.0)
        add_clip_to_track(proj, 1, "clip1", position=5.0, out_point=20.0)
        add_clip_to_track(proj, 2, "clip2", position=0.0, out_point=60.0)

        add_filter(proj, 0, 0, "brightness", {"level": 1.2})
        add_transition(proj, "dissolve", 0, 1, position=5.0, duration=2.0)
        add_guide(proj, 0.0, label="Start")
        add_guide(proj, 30.0, label="End")

        return proj

    def _parse(self, proj=None):
        proj = proj or self._make_full_project()
        return ET.fromstring(generate_kdenlive_xml(proj))

    def test_xml_is_string(self):
        proj = self._make_full_project()
        xml = generate_kdenlive_xml(proj)
        assert isinstance(xml, str)

    def test_xml_has_mlt_root(self):
        root = self._parse()
        assert root.tag == "mlt"

    def test_xml_has_profile(self):
        root = self._parse()
        profile = root.find("profile")
        assert profile is not None
        assert profile.get("width") == "1920"
        assert profile.get("height") == "1080"
        assert profile.get("frame_rate_num") == "30"

    def test_xml_has_chains_for_clips(self):
        root = self._parse()
        chains = root.findall("chain")
        sources = [c.find("property[@name='resource']").text for c in chains if c.find("property[@name='resource']") is not None]
        assert any("interview.mp4" in s for s in sources)

    def test_xml_has_playlists(self):
        root = self._parse()
        playlists = root.findall("playlist")
        ids = [p.get("id") for p in playlists]
        assert "playlist0" in ids
        assert "playlist1" in ids

    def test_xml_has_sequence_tractor(self):
        root = self._parse()
        seq = _find_sequence(root)
        assert seq is not None
        assert seq.find("property[@name='kdenlive:uuid']") is not None

    def test_xml_has_filters(self):
        root = self._parse()
        filters = [
            f for f in root.findall(".//entry/filter")
            if any(p.text == "brightness" for p in f.findall("property[@name='mlt_service']"))
        ]
        assert len(filters) > 0

    def test_xml_has_user_transition(self):
        root = self._parse()
        seq = _find_sequence(root)
        luma = seq.findall("transition[@mlt_service='luma']")
        assert len(luma) == 1

    def test_xml_has_guides_in_sequence(self):
        root = self._parse()
        seq = _find_sequence(root)
        guides_prop = seq.find("property[@name='kdenlive:sequenceproperties.guides']")
        assert guides_prop is not None
        data = json.loads(guides_prop.text)
        assert len(data) == 2
        assert data[0]["comment"] == "Start"
        assert data[1]["comment"] == "End"

    def test_xml_empty_project(self):
        proj = create_project()
        root = ET.fromstring(generate_kdenlive_xml(proj))
        assert root.tag == "mlt"
        assert root.find("profile") is not None

    def test_xml_special_characters_escaped(self):
        proj = create_project(name='Test "Project" <1>')
        root = ET.fromstring(generate_kdenlive_xml(proj))
        assert root.get("title") == 'Test "Project" <1>'

    def test_xml_clip_type_numbers(self):
        proj = create_project()
        import_clip(proj, "/a.mp4", name="V", clip_type="video", duration=10.0)
        import_clip(proj, "/b.mp3", name="A", clip_type="audio", duration=10.0)
        import_clip(proj, "/c.jpg", name="I", clip_type="image", duration=5.0)
        root = ET.fromstring(generate_kdenlive_xml(proj))
        type_nums = set()
        for chain in root.findall("chain"):
            ct = chain.find("property[@name='kdenlive:clip_type']")
            if ct is not None:
                type_nums.add(ct.text)
        assert "0" in type_nums  # video
        assert "1" in type_nums  # audio
        assert "2" in type_nums  # image

    def test_xml_sd_pal_profile(self):
        proj = create_project(profile="sd_pal")
        root = ET.fromstring(generate_kdenlive_xml(proj))
        profile = root.find("profile")
        assert profile.get("width") == "720"
        assert profile.get("height") == "576"
        assert profile.get("progressive") == "0"
