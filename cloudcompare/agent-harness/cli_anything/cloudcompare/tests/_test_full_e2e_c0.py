# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _resolve_cli, cloud_xyz, tmp_dir  # noqa: F401,E501


class _TestCLISubprocessMixin0:
    CLI_BASE = _resolve_cli("cli-anything-cloudcompare")
    def _run(self, args, check=True, allow_fail=False):
        result = subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
        )
        if check and not allow_fail and result.returncode != 0:
            pytest.fail(
                f"CLI failed (exit {result.returncode}):\n"
                f"  stdout: {result.stdout[:400]}\n"
                f"  stderr: {result.stderr[:400]}"
            )
        return result
    def test_help(self):
        """--help exits 0 and shows usage."""
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "cloudcompare" in result.stdout.lower() or "Usage" in result.stdout
    def test_info_json(self):
        """info --json returns valid JSON with expected keys."""
        result = self._run(["--json", "info"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "cloudcompare_available" in data
        assert "supported_cloud_formats" in data
        print(f"\n  CloudCompare available: {data['cloudcompare_available']}")
        print(f"  Command: {data.get('command')}")
    def test_project_new_creates_file(self, tmp_dir):
        """project new -o creates a valid JSON project file."""
        proj_path = os.path.join(tmp_dir, "cli_test.json")
        result = self._run(["--json", "project", "new", "-o", proj_path])
        assert result.returncode == 0
        assert os.path.exists(proj_path)
        data = json.loads(result.stdout)
        assert "cloud_count" in data
        assert data["cloud_count"] == 0
        print(f"\n  Project created: {proj_path}")
    def test_project_info_json(self, tmp_dir):
        """project info --json returns JSON with project details."""
        proj_path = os.path.join(tmp_dir, "info_test.json")
        # Create project first
        self._run(["project", "new", "-o", proj_path])
        # Query info
        result = self._run(["--json", "--project", proj_path, "project", "info"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "cloud_count" in data
        assert "mesh_count" in data
        assert "settings" in data
    def test_cloud_add_and_list(self, tmp_dir, cloud_xyz):
        """cloud add adds the cloud; cloud list returns it."""
        proj_path = os.path.join(tmp_dir, "cloud_test.json")
        self._run(["project", "new", "-o", proj_path])
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz, "--label", "scan_a"])
        result = self._run(["--json", "--project", proj_path, "cloud", "list"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["count"] == 1
        assert data["clouds"][0]["label"] == "scan_a"
    def test_export_formats_json(self):
        """export formats --json returns cloud and mesh format lists."""
        result = self._run(["--json", "export", "formats"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "cloud" in data
        assert "mesh" in data
        assert "las" in data["cloud"]
        assert "obj" in data["mesh"]
    def test_session_history_json(self, tmp_dir):
        """session history --json returns JSON history list."""
        proj_path = os.path.join(tmp_dir, "hist_test.json")
        self._run(["project", "new", "-o", proj_path])
        result = self._run(["--json", "--project", proj_path, "session", "history"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "history" in data
        assert "count" in data
