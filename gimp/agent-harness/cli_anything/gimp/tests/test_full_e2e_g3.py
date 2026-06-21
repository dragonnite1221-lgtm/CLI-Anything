# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-gimp")

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
        assert "GIMP CLI" in result.stdout

    def test_project_new(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["project", "new", "-o", out])
        assert result.returncode == 0
        assert os.path.exists(out)

    def test_project_new_json(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["--json", "project", "new", "-o", out])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["canvas"]["width"] == 1920

    def test_project_profiles(self):
        result = self._run(["project", "profiles"])
        assert result.returncode == 0
        assert "hd1080p" in result.stdout

    def test_filter_list_available(self):
        result = self._run(["filter", "list-available"])
        assert result.returncode == 0
        assert "brightness" in result.stdout

    def test_export_presets(self):
        result = self._run(["export", "presets"])
        assert result.returncode == 0
        assert "png" in result.stdout

    def test_full_workflow_json(self, tmp_dir, sample_image):
        proj_path = os.path.join(tmp_dir, "workflow.json")
        out_path = os.path.join(tmp_dir, "output.png")

        # Create project
        self._run(
            ["--json", "project", "new", "-o", proj_path, "-w", "300", "-h", "200"]
        )

        # Add layer
        self._run(
            ["--json", "--project", proj_path, "layer", "add-from-file", sample_image]
        )

        # Save
        self._run(["--project", proj_path, "project", "save"])

        # Export
        self._run(["--project", proj_path, "export", "render", out_path, "--overwrite"])

        assert os.path.exists(out_path)
        result = Image.open(out_path)
        assert result.size == (300, 200)
