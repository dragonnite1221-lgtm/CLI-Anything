# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p2 import TestXMLParsing  # noqa: F401,E501


class TestExportVerification:
    def test_ext_to_format(self):
        assert _ext_to_format(".pdf") == "pdf"
        assert _ext_to_format(".mid") == "midi"
        assert _ext_to_format(".mp3") == "mp3"
        assert _ext_to_format(".musicxml") == "musicxml"

    def test_verify_nonexistent(self):
        result = verify_output("/nonexistent/file.pdf")
        assert not result["exists"]
        assert not result["valid"]

    def test_verify_pdf(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 test content")
            tmp = f.name
        try:
            result = verify_output(tmp, "pdf")
            assert result["exists"]
            assert result["valid"]
        finally:
            os.unlink(tmp)

    def test_verify_midi(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            f.write(b"MThd\x00\x00\x00\x06")
            tmp = f.name
        try:
            result = verify_output(tmp, "midi")
            assert result["exists"]
            assert result["valid"]
        finally:
            os.unlink(tmp)

    def test_verify_mp3_sync(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"\xff\xfb\x90\x00" + b"\x00" * 100)
            tmp = f.name
        try:
            result = verify_output(tmp, "mp3")
            assert result["valid"]
        finally:
            os.unlink(tmp)

    def test_verify_mp3_id3(self):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"ID3" + b"\x00" * 100)
            tmp = f.name
        try:
            result = verify_output(tmp, "mp3")
            assert result["valid"]
        finally:
            os.unlink(tmp)

    def test_verify_png(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            tmp = f.name
        try:
            result = verify_output(tmp, "png")
            assert result["valid"]
        finally:
            os.unlink(tmp)

    def test_verify_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp = f.name
        try:
            result = verify_output(tmp, "pdf")
            assert result["exists"]
            assert not result["valid"]
        finally:
            os.unlink(tmp)


class TestMediaStats:
    def test_score_stats_from_mxl(self):
        """Create a synthetic .mxl and test stats extraction."""
        tree = TestXMLParsing()._make_musicxml(
            fifths=0, num_measures=8, num_notes=32, title="Stats Test"
        )
        xml_str = ET.tostring(tree.getroot(), encoding="unicode",
                              xml_declaration=True)

        with tempfile.NamedTemporaryFile(suffix=".mxl", delete=False) as f:
            tmp_path = f.name

        try:
            with zipfile.ZipFile(tmp_path, "w") as zf:
                zf.writestr("score.xml", xml_str)

            from cli_anything.musescore.core.media import score_stats
            result = score_stats(tmp_path)
            assert result["format"] == "mxl"
            assert result["stats"]["measures"] == 8
            assert result["stats"]["notes"] == 32
            assert result["stats"]["title"] == "Stats Test"
            assert result["stats"]["key_signature"] == 0
            assert result["stats"]["key_name"] == "C major"
        finally:
            os.unlink(tmp_path)
