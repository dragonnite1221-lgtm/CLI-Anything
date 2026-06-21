# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestXMLParsing:
    def _make_musicxml(self, fifths=-5, beats="4", beat_type="4",
                       title="Test Score", num_measures=4, num_notes=16):
        """Create a synthetic MusicXML tree for testing."""
        root = ET.Element("score-partwise", version="4.0")
        # Work title
        work = ET.SubElement(root, "work")
        ET.SubElement(work, "work-title").text = title
        # Part list
        part_list = ET.SubElement(root, "part-list")
        sp = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(sp, "part-name").text = "Piano"
        si = ET.SubElement(sp, "score-instrument", id="P1-I1")
        ET.SubElement(si, "instrument-name").text = "Piano"
        # Part with measures
        part = ET.SubElement(root, "part", id="P1")
        for m in range(num_measures):
            measure = ET.SubElement(part, "measure", number=str(m + 1))
            if m == 0:
                attrs = ET.SubElement(measure, "attributes")
                key = ET.SubElement(attrs, "key")
                ET.SubElement(key, "fifths").text = str(fifths)
                time = ET.SubElement(attrs, "time")
                ET.SubElement(time, "beats").text = beats
                ET.SubElement(time, "beat-type").text = beat_type
            for n in range(num_notes // num_measures):
                note = ET.SubElement(measure, "note")
                pitch = ET.SubElement(note, "pitch")
                ET.SubElement(pitch, "step").text = "C"
                ET.SubElement(pitch, "octave").text = "4"
        return ET.ElementTree(root)

    def test_get_key_signature(self):
        tree = self._make_musicxml(fifths=-5)
        assert get_key_signature(tree) == -5

    def test_get_time_signature(self):
        tree = self._make_musicxml(beats="3", beat_type="4")
        assert get_time_signature(tree) == "3/4"

    def test_get_instruments(self):
        tree = self._make_musicxml()
        instruments = get_instruments(tree)
        assert len(instruments) == 1
        assert instruments[0]["name"] == "Piano"

    def test_get_score_title(self):
        tree = self._make_musicxml(title="My Score")
        assert get_score_title(tree) == "My Score"

    def test_count_measures(self):
        tree = self._make_musicxml(num_measures=8)
        assert count_measures(tree) == 8

    def test_count_notes(self):
        tree = self._make_musicxml(num_measures=4, num_notes=16)
        assert count_notes(tree) == 16

    def test_detect_format(self):
        assert detect_format("score.mscz") == "mscz"
        assert detect_format("score.mxl") == "mxl"
        assert detect_format("score.musicxml") == "musicxml"
        assert detect_format("score.mid") == "mid"
        assert detect_format("score.txt") == "unknown"

    def test_mscz_roundtrip(self):
        """Test writing and reading a .mscz file."""
        tree = self._make_musicxml()
        data = {
            "mscx": tree,
            "mscx_filename": "score.mscx",
            "style": "<Style></Style>",
            "audio_settings": '{"master_gain": 1.0}',
            "view_settings": '{"zoom": 100}',
            "other_files": {},
        }
        with tempfile.NamedTemporaryFile(suffix=".mscz", delete=False) as f:
            tmp_path = f.name

        try:
            write_mscz(tmp_path, data)
            assert os.path.isfile(tmp_path)

            # Verify it's a valid ZIP
            assert zipfile.is_zipfile(tmp_path)

            # Read back
            read_data = read_mscz(tmp_path)
            assert read_data["mscx"] is not None
            assert read_data["style"] == "<Style></Style>"
            assert get_key_signature(read_data["mscx"]) == -5
        finally:
            os.unlink(tmp_path)
