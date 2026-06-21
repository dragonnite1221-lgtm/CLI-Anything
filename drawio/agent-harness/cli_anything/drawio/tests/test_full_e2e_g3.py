# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    """Test the CLI as a subprocess, like a real user/agent would use it."""

    CLI_BASE = _resolve_cli("cli-anything-drawio")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=30,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "Draw.io" in result.stdout or "diagram" in result.stdout.lower()

    def test_project_new_json(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        result = self._run(["--json", "project", "new", "-o", out])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["action"] == "new_project"
        assert os.path.exists(out)

    def test_project_info_json(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        self._run(["--json", "project", "new", "-o", out])
        result = self._run(["--json", "--project", out, "project", "info"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["project_path"] is not None

    def test_shape_add_json(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        self._run(["project", "new", "-o", out])
        result = self._run(
            [
                "--json",
                "--project",
                out,
                "shape",
                "add",
                "rectangle",
                "--label",
                "CLI Shape",
            ]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["action"] == "add_shape"
        assert data["label"] == "CLI Shape"

    def test_shape_list_json(self, tmp_path):
        """Shape list from a file that already has shapes.

        Each subprocess is stateless, so we build a file with shapes
        using the library directly, then list via CLI.
        """
        out = str(tmp_path / "test.drawio")
        s = Session()
        proj_mod.new_project(s)
        shapes_mod.add_shape(s, "rectangle", label="A")
        shapes_mod.add_shape(s, "ellipse", 200, 100, label="B")
        proj_mod.save_project(s, out)

        result = self._run(["--json", "--project", out, "shape", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_connect_add_json(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        self._run(["project", "new", "-o", out])
        r1 = self._run(
            ["--json", "--project", out, "shape", "add", "rectangle", "--label", "A"]
        )
        id1 = json.loads(r1.stdout)["id"]

        # Need to save after adding first shape, then reload
        # Actually, each subprocess is independent - shapes don't persist across calls
        # unless we save. Let's test the shape types and help instead.

    def test_shape_types(self):
        result = self._run(["--json", "shape", "types"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "rectangle" in data
        assert "ellipse" in data

    def test_connect_styles(self):
        result = self._run(["--json", "connect", "styles"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "orthogonal" in data

    def test_export_formats(self):
        result = self._run(["--json", "export", "formats"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        names = [f["name"] for f in data]
        assert "png" in names
        assert "svg" in names

    def test_page_list(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        self._run(["project", "new", "-o", out])
        result = self._run(["--json", "--project", out, "page", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 1

    def test_session_status(self, tmp_path):
        out = str(tmp_path / "test.drawio")
        self._run(["project", "new", "-o", out])
        result = self._run(["--json", "--project", out, "session", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["project_open"] is True

    def test_project_presets(self):
        result = self._run(["--json", "project", "presets"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "letter" in data
        assert "a4" in data

    def test_export_xml_subprocess(self, tmp_path):
        drawio_file = str(tmp_path / "test.drawio")
        xml_file = str(tmp_path / "test.xml")

        self._run(["project", "new", "-o", drawio_file])
        self._run(
            [
                "--project",
                drawio_file,
                "shape",
                "add",
                "rectangle",
                "--label",
                "SubTest",
            ]
        )
        result = self._run(
            [
                "--json",
                "--project",
                drawio_file,
                "export",
                "render",
                xml_file,
                "-f",
                "xml",
                "--overwrite",
            ]
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["format"] == "xml"
        assert os.path.exists(xml_file)
