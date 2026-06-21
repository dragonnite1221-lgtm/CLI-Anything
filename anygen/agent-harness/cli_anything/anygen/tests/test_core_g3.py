# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExportVerify:
    def test_verify_missing_file(self):
        r = verify_file("/nonexistent/file.pptx")
        assert not r["valid"]

    def test_verify_empty_file(self, tmp_path):
        f = tmp_path / "empty.pptx"
        f.write_bytes(b"")
        r = verify_file(str(f))
        assert not r["valid"]

    def test_verify_valid_pptx(self, tmp_path):
        f = tmp_path / "test.pptx"
        with zipfile.ZipFile(f, "w") as zf:
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
            zf.writestr("ppt/presentation.xml", "<p/>")
        r = verify_file(str(f))
        assert r["valid"]
        assert r["format"] == "OOXML"

    def test_verify_valid_docx(self, tmp_path):
        f = tmp_path / "test.docx"
        with zipfile.ZipFile(f, "w") as zf:
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
            zf.writestr("word/document.xml", "<w/>")
        r = verify_file(str(f))
        assert r["valid"]

    def test_verify_valid_pdf(self, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_bytes(b"%PDF-1.4 fake pdf content")
        r = verify_file(str(f))
        assert r["valid"]
        assert r["format"] == "PDF"

    def test_verify_valid_png(self, tmp_path):
        f = tmp_path / "test.png"
        f.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        r = verify_file(str(f))
        assert r["valid"]
        assert r["format"] == "PNG"

    def test_verify_valid_svg(self, tmp_path):
        f = tmp_path / "test.svg"
        f.write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle/></svg>')
        r = verify_file(str(f))
        assert r["valid"]

    def test_verify_corrupt_zip(self, tmp_path):
        f = tmp_path / "bad.pptx"
        f.write_bytes(b"PK\x03\x04" + b"\x00" * 50)
        r = verify_file(str(f))
        assert not r["valid"]
