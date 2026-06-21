# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestKdenliveGen5FormatMixin0:
    """Validate Kdenlive Gen 5 (doc version 1.1) XML structure."""
    def _make_simple_project(self):
        proj = create_project(name="Gen5Test", profile="hd1080p30")
        import_clip(proj, "/video.mp4", name="Video", duration=30.0)
        import_clip(proj, "/audio.mp3", name="Audio", duration=60.0, clip_type="audio")
        add_track(proj, name="V1", track_type="video")
        add_track(proj, name="A1", track_type="audio")
        add_clip_to_track(proj, 0, "clip0", position=0.0, out_point=15.0)
        add_clip_to_track(proj, 1, "clip1", position=0.0, out_point=30.0)
        add_transition(proj, "dissolve", 0, 1, position=5.0, duration=2.0)
        add_guide(proj, 10.0, label="Marker")
        return proj
    def _parse(self, proj=None):
        proj = proj or self._make_simple_project()
        return ET.fromstring(generate_kdenlive_xml(proj))
    def test_mlt_root_producer_is_main_bin(self):
        root = self._parse()
        assert root.get("producer") == "main_bin"
    def test_has_main_bin_playlist(self):
        root = self._parse()
        assert root.find(".//playlist[@id='main_bin']") is not None
    def test_main_bin_has_docproperties(self):
        root = self._parse()
        main_bin = root.find(".//playlist[@id='main_bin']")
        props = {p.get("name"): p.text for p in main_bin.findall("property")}
        assert props.get("kdenlive:docproperties.version") == "1.1"
        assert "kdenlive:docproperties.uuid" in props
    def test_main_bin_lists_bin_clip_chains(self):
        root = self._parse()
        main_bin = root.find(".//playlist[@id='main_bin']")
        entries = main_bin.findall("entry")
        producer_refs = [e.get("producer") for e in entries]
        # Bin clips should be referenced as chainN (not *_bin)
        bin_refs = [r for r in producer_refs if r.startswith("chain")]
        assert len(bin_refs) == 2
    def test_main_bin_lists_sequence(self):
        root = self._parse()
        seq = _find_sequence(root)
        assert seq is not None
        seq_id = seq.get("id")
        main_bin = root.find(".//playlist[@id='main_bin']")
        entries = main_bin.findall("entry")
        producer_refs = [e.get("producer") for e in entries]
        assert seq_id in producer_refs
    def test_per_track_tractor_wraps_playlists(self):
        root = self._parse()
        tractor0 = root.find(".//tractor[@id='tractor0']")
        assert tractor0 is not None
        tracks = tractor0.findall("track")
        assert len(tracks) == 2  # dual playlist
        producers = [t.get("producer") for t in tracks]
        assert any(p.startswith("playlist") for p in producers)
    def test_video_track_hides_audio(self):
        root = self._parse()
        tractor0 = root.find(".//tractor[@id='tractor0']")
        tracks = tractor0.findall("track")
        assert all(t.get("hide") == "audio" for t in tracks)
    def test_audio_track_hides_video(self):
        root = self._parse()
        tractor1 = root.find(".//tractor[@id='tractor1']")
        tracks = tractor1.findall("track")
        assert all(t.get("hide") == "video" for t in tracks)
    def test_sequence_tractor_has_uuid(self):
        root = self._parse()
        seq = _find_sequence(root)
        assert seq is not None
        uuid_val = seq.get("id")
        assert re.match(r'^\{[0-9a-f-]+\}$', uuid_val)
        uuid_prop = seq.find("property[@name='kdenlive:uuid']")
        assert uuid_prop is not None
        assert uuid_prop.text == uuid_val
    def test_sequence_tractor_references_track_tractors(self):
        root = self._parse()
        seq = _find_sequence(root)
        track_refs = [t.get("producer") for t in seq.findall("track")]
        assert "producer0" in track_refs  # black track first
        assert "tractor0" in track_refs
        assert "tractor1" in track_refs
    def test_project_tractor_exists(self):
        root = self._parse()
        assert root.find(".//tractor[@id='tractor_project']") is not None
    def test_project_tractor_has_property(self):
        root = self._parse()
        proj_tractor = root.find(".//tractor[@id='tractor_project']")
        props = {p.get("name"): p.text for p in proj_tractor.findall("property")}
        assert props.get("kdenlive:projectTractor") == "1"
    def test_project_tractor_references_sequence(self):
        root = self._parse()
        seq = _find_sequence(root)
        seq_id = seq.get("id")
        proj_tractor = root.find(".//tractor[@id='tractor_project']")
        track = proj_tractor.find("track")
        assert track.get("producer") == seq_id
    def test_internal_transitions_in_sequence(self):
        root = self._parse()
        seq = _find_sequence(root)
        transitions = seq.findall("transition")
        mix_trans = [t for t in transitions if t.find("property[@name='mlt_service']") is not None and t.find("property[@name='mlt_service']").text == "mix"]
        blend_trans = [t for t in transitions if t.find("property[@name='mlt_service']") is not None and t.find("property[@name='mlt_service']").text == "qtblend"]
        assert len(mix_trans) >= 1  # audio track gets mix
        assert len(blend_trans) >= 1  # video track gets qtblend
    def test_user_transition_in_sequence(self):
        root = self._parse()
        seq = _find_sequence(root)
        luma = seq.findall("transition[@mlt_service='luma']")
        assert len(luma) == 1
