# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@requires_mscore
@requires_samples
class TestExportE2E:
    def test_export_pdf(self):
        """Export MXL to PDF, verify magic bytes."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.export import export_score, verify_output

            export_score(str(_SAMPLE_MXL), out, fmt="pdf")
            result = verify_output(out, "pdf")
            assert result["valid"], f"PDF verification failed: {result}"
            print(f"  PDF output: {out} ({result['size']} bytes)")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_export_midi(self):
        """Export MXL to MIDI, verify magic bytes."""
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.export import export_score, verify_output

            export_score(str(_SAMPLE_MXL), out, fmt="midi")
            result = verify_output(out, "midi")
            assert result["valid"], f"MIDI verification failed: {result}"
            print(f"  MIDI output: {out} ({result['size']} bytes)")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_export_mp3(self):
        """Export MXL to MP3, verify magic bytes."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.export import export_score, verify_output

            export_score(str(_SAMPLE_MXL), out, fmt="mp3", bitrate=128)
            result = verify_output(out, "mp3")
            assert result["valid"], f"MP3 verification failed: {result}"
            print(f"  MP3 output: {out} ({result['size']} bytes)")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_export_musicxml(self):
        """Export MSCZ to MusicXML, verify XML structure."""
        with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.export import export_score

            export_score(str(_SAMPLE_MSCZ), out, fmt="musicxml")
            import xml.etree.ElementTree as ET

            tree = ET.parse(out)
            assert tree.getroot().tag == "score-partwise"
            print(f"  MusicXML output: {out}")
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_export_png(self):
        """Export MXL to PNG, verify at least one page produced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "output.png")
            from cli_anything.musescore.core.export import export_score

            export_score(str(_SAMPLE_MXL), out, fmt="png", dpi=72)
            # mscore produces output-1.png, output-2.png, etc.
            pngs = list(Path(tmpdir).glob("*.png"))
            assert len(pngs) >= 1, f"No PNG files produced in {tmpdir}"
            # Verify first PNG magic bytes
            with open(pngs[0], "rb") as f:
                header = f.read(4)
            assert header == b"\x89PNG", f"Invalid PNG header: {header}"
            print(f"  PNG pages: {len(pngs)}")


@requires_mscore
@requires_samples
class TestTransposeE2E:
    def test_transpose_g_to_c(self):
        """Transpose G major MXL to C major, verify key signature."""
        with tempfile.NamedTemporaryFile(suffix=".mscz", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.transpose import transpose_by_key

            result = transpose_by_key(
                str(_SAMPLE_MXL),
                out,
                target_key="C major",
                direction="closest",
            )
            assert result["target_key_int"] == 0

            # Export to MusicXML and check key signature
            with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as fx:
                xml_out = fx.name
            from cli_anything.musescore.core.export import export_score

            export_score(out, xml_out, fmt="musicxml")

            from cli_anything.musescore.utils.mscx_xml import (
                read_score_tree,
                get_key_signature,
            )

            tree = read_score_tree(xml_out)
            keysig = get_key_signature(tree)
            assert keysig == 0, f"Expected keysig=0 (C major), got {keysig}"
            print(f"  Transposed G→C: keysig={keysig}")
            os.unlink(xml_out)
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_transpose_by_interval(self):
        """Transpose by 2 semitones (major second up)."""
        with tempfile.NamedTemporaryFile(suffix=".mscz", delete=False) as f:
            out = f.name
        try:
            from cli_anything.musescore.core.transpose import transpose_by_interval

            result = transpose_by_interval(
                str(_SAMPLE_MXL),
                out,
                semitones=2,
                direction="up",
            )
            assert result["mode"] == "by_interval"
            assert os.path.isfile(out)
            print(f"  Transposed by +2 semitones: {out}")
        finally:
            if os.path.exists(out):
                os.unlink(out)
