# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocessE2E:
    """True E2E via subprocess: invoke the installed CLI to produce real files."""

    CLI_BASE = _resolve_cli("cli-anything-libreoffice")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_full_writer_pdf_workflow(self, tmp_dir):
        """CLI subprocess: create writer doc, add content, export to PDF."""
        proj_path = os.path.join(tmp_dir, "cli_test.json")
        pdf_path = os.path.join(tmp_dir, "cli_output.pdf")

        # Create project
        self._run(
            [
                "document",
                "new",
                "-o",
                proj_path,
                "--type",
                "writer",
                "-n",
                "CLI PDF Test",
            ]
        )
        # Add content
        self._run(
            [
                "--project",
                proj_path,
                "writer",
                "add-heading",
                "-t",
                "CLI Generated",
                "-l",
                "1",
            ]
        )
        self._run(
            [
                "--project",
                proj_path,
                "writer",
                "add-paragraph",
                "-t",
                "This PDF was generated entirely via the CLI subprocess.",
            ]
        )
        # Save
        self._run(["--project", proj_path, "document", "save"])
        # Export to PDF
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                pdf_path,
                "-p",
                "pdf",
                "--overwrite",
            ]
        )

        assert os.path.exists(pdf_path), f"PDF not created at {pdf_path}"
        size = os.path.getsize(pdf_path)
        assert size > 0, "PDF is empty"
        with open(pdf_path, "rb") as f:
            assert f.read(5) == b"%PDF-", "Not a valid PDF"
        print(f"\n  CLI PDF: {pdf_path} ({size:,} bytes)")

    def test_full_calc_xlsx_workflow(self, tmp_dir):
        """CLI subprocess: create calc doc, set cells, export to XLSX."""
        proj_path = os.path.join(tmp_dir, "calc_test.json")
        xlsx_path = os.path.join(tmp_dir, "calc_output.xlsx")

        self._run(["document", "new", "-o", proj_path, "--type", "calc"])
        self._run(["--project", proj_path, "calc", "set-cell", "A1", "Name"])
        self._run(["--project", proj_path, "calc", "set-cell", "B1", "Score"])
        self._run(["--project", proj_path, "calc", "set-cell", "A2", "Alice"])
        self._run(
            ["--project", proj_path, "calc", "set-cell", "B2", "95", "--type", "float"]
        )
        self._run(["--project", proj_path, "document", "save"])
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                xlsx_path,
                "-p",
                "xlsx",
                "--overwrite",
            ]
        )

        assert os.path.exists(xlsx_path), f"XLSX not created at {xlsx_path}"
        assert zipfile.is_zipfile(xlsx_path), "XLSX is not a valid ZIP"
        print(f"\n  CLI XLSX: {xlsx_path} ({os.path.getsize(xlsx_path):,} bytes)")

    def test_full_impress_pptx_workflow(self, tmp_dir):
        """CLI subprocess: create presentation, add slides, export to PPTX."""
        proj_path = os.path.join(tmp_dir, "impress_test.json")
        pptx_path = os.path.join(tmp_dir, "impress_output.pptx")

        self._run(["document", "new", "-o", proj_path, "--type", "impress"])
        self._run(["--project", proj_path, "impress", "add-slide", "-t", "Welcome"])
        self._run(
            [
                "--project",
                proj_path,
                "impress",
                "add-slide",
                "-t",
                "Agenda",
                "-c",
                "Overview",
            ]
        )
        self._run(["--project", proj_path, "document", "save"])
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                pptx_path,
                "-p",
                "pptx",
                "--overwrite",
            ]
        )

        assert os.path.exists(pptx_path), f"PPTX not created at {pptx_path}"
        assert zipfile.is_zipfile(pptx_path), "PPTX is not a valid ZIP"
        print(f"\n  CLI PPTX: {pptx_path} ({os.path.getsize(pptx_path):,} bytes)")

    def test_full_writer_docx_workflow(self, tmp_dir):
        """CLI subprocess: writer -> DOCX via LibreOffice headless."""
        proj_path = os.path.join(tmp_dir, "docx_test.json")
        docx_path = os.path.join(tmp_dir, "docx_output.docx")

        self._run(
            ["document", "new", "-o", proj_path, "--type", "writer", "-n", "DOCX Test"]
        )
        self._run(
            [
                "--project",
                proj_path,
                "writer",
                "add-heading",
                "-t",
                "DOCX via CLI",
                "-l",
                "1",
            ]
        )
        self._run(
            [
                "--project",
                proj_path,
                "writer",
                "add-paragraph",
                "-t",
                "Full E2E through subprocess.",
            ]
        )
        self._run(["--project", proj_path, "document", "save"])
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                docx_path,
                "-p",
                "docx",
                "--overwrite",
            ]
        )

        assert os.path.exists(docx_path)
        assert zipfile.is_zipfile(docx_path)
        print(f"\n  CLI DOCX: {docx_path} ({os.path.getsize(docx_path):,} bytes)")
