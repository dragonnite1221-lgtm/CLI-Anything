# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    """Test the installed cli-anything-krita command via subprocess."""

    CLI_BASE = _resolve_cli("cli-anything-krita")

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
        assert "krita" in result.stdout.lower()

    def test_project_new_json(self, tmp_dir):
        out = os.path.join(tmp_dir, "test.json")
        result = self._run(["--json", "project", "new", "-n", "SubTest", "-o", out])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "created"
        assert data["name"] == "SubTest"
        assert os.path.exists(out)

    def test_layer_workflow(self, tmp_dir):
        proj_path = os.path.join(tmp_dir, "layers.json")
        self._run(["--json", "project", "new", "-o", proj_path])
        self._run(["--json", "--project", proj_path, "layer", "add", "Sketch"])
        self._run(
            [
                "--json",
                "--project",
                proj_path,
                "layer",
                "add",
                "Colors",
                "--opacity",
                "200",
            ]
        )

        result = self._run(["--json", "--project", proj_path, "layer", "list"])
        layers = json.loads(result.stdout)
        assert len(layers) == 3  # Background + Sketch + Colors
        names = [l["name"] for l in layers]
        assert "Sketch" in names
        assert "Colors" in names

    def test_export_presets(self):
        result = self._run(["--json", "export", "presets"])
        assert result.returncode == 0
        presets = json.loads(result.stdout)
        assert len(presets) > 0

    def test_filter_list(self):
        result = self._run(["--json", "filter", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "filters" in data
        assert len(data["filters"]) > 0

    def test_status(self):
        result = self._run(["--json", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "project_loaded" in data

    def test_full_workflow(self, tmp_dir):
        """Full workflow: create → layers → filter → export .kra."""
        proj_path = os.path.join(tmp_dir, "full.json")

        # Create project
        r = self._run(
            [
                "--json",
                "project",
                "new",
                "-n",
                "FullTest",
                "-w",
                "512",
                "-h",
                "512",
                "-o",
                proj_path,
            ]
        )
        assert r.returncode == 0

        # Add layers
        self._run(["--json", "-p", proj_path, "layer", "add", "Sketch"])
        self._run(
            ["--json", "-p", proj_path, "layer", "add", "Paint", "--opacity", "220"]
        )

        # Apply filter
        self._run(["--json", "-p", proj_path, "filter", "apply", "blur", "-l", "Paint"])

        # Get info
        r = self._run(["--json", "-p", proj_path, "project", "info"])
        assert r.returncode == 0
        info = json.loads(r.stdout)
        assert info["layer_count"] == 3

        # Canvas resize
        self._run(
            ["--json", "-p", proj_path, "canvas", "resize", "-w", "1024", "-h", "1024"]
        )
        r = self._run(["--json", "-p", proj_path, "canvas", "info"])
        canvas = json.loads(r.stdout)
        assert canvas["width"] == 1024

        print(f"\n  Full workflow test passed. Project: {proj_path}")
