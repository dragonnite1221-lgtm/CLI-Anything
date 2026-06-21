# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-libreoffice")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "LibreOffice CLI" in result.stdout

    def test_document_new(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["document", "new", "-o", out])
        assert result.returncode == 0
        assert os.path.exists(out)

    def test_document_new_json(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["--json", "document", "new", "-o", out])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["type"] == "writer"

    def test_document_profiles(self):
        result = self._run(["document", "profiles"])
        assert result.returncode == 0
        assert "a4_portrait" in result.stdout

    def test_export_presets(self):
        result = self._run(["export", "presets"])
        assert result.returncode == 0
        assert "odt" in result.stdout

    def test_open_existing_odt_to_project_and_edit(self, tmp_dir):
        source_proj = create_document(doc_type="writer", name="Existing")
        add_heading(source_proj, text="Existing Heading", level=1)
        add_paragraph(source_proj, text="Original paragraph")
        source_odt = os.path.join(tmp_dir, "existing.odt")
        imported_json = os.path.join(tmp_dir, "imported.json")
        edited_odt = os.path.join(tmp_dir, "edited.odt")
        to_odt(source_proj, source_odt)

        result = self._run(
            [
                "--json",
                "document",
                "open",
                source_odt,
                "-o",
                imported_json,
            ]
        )
        data = json.loads(result.stdout)
        assert data["type"] == "writer"
        assert data["content_count"] == 2
        assert os.path.exists(imported_json)

        self._run(
            [
                "--project",
                imported_json,
                "writer",
                "add-paragraph",
                "-t",
                "Added after import",
            ]
        )
        self._run(
            [
                "--project",
                imported_json,
                "export",
                "render",
                edited_odt,
                "-p",
                "odt",
                "--overwrite",
            ]
        )

        parsed = parse_odf(edited_odt)
        assert "Existing Heading" in parsed["content_xml"]
        assert "Added after import" in parsed["content_xml"]

    def test_full_workflow(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "workflow.json")
        odt_path = os.path.join(tmp_dir, "output.odt")

        # Create project
        self._run(
            [
                "--json",
                "document",
                "new",
                "-o",
                proj_path,
                "--type",
                "writer",
                "-n",
                "Workflow",
            ]
        )

        # Add content
        self._run(
            ["--project", proj_path, "writer", "add-heading", "-t", "Title", "-l", "1"]
        )

        # Save
        self._run(["--project", proj_path, "document", "save"])

        # Export to ODF
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                odt_path,
                "-p",
                "odt",
                "--overwrite",
            ]
        )

        assert os.path.exists(odt_path)
        result = validate_odf(odt_path)
        assert result["valid"] is True

    def test_calc_workflow(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "calc.json")
        ods_path = os.path.join(tmp_dir, "output.ods")

        self._run(["document", "new", "--type", "calc", "-o", proj_path])
        self._run(["--project", proj_path, "calc", "set-cell", "A1", "Hello"])
        self._run(["--project", proj_path, "document", "save"])
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                ods_path,
                "-p",
                "ods",
                "--overwrite",
            ]
        )

        assert os.path.exists(ods_path)
        result = validate_odf(ods_path)
        assert result["valid"] is True

    def test_impress_workflow(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "impress.json")
        odp_path = os.path.join(tmp_dir, "output.odp")

        self._run(["document", "new", "--type", "impress", "-o", proj_path])
        self._run(["--project", proj_path, "impress", "add-slide", "-t", "Welcome"])
        self._run(["--project", proj_path, "document", "save"])
        self._run(
            [
                "--project",
                proj_path,
                "export",
                "render",
                odp_path,
                "-p",
                "odp",
                "--overwrite",
            ]
        )

        assert os.path.exists(odp_path)
        result = validate_odf(odp_path)
        assert result["valid"] is True
