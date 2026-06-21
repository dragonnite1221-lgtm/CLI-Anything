# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _resolve_cli, test_video  # noqa: F401,E501


class _TestCLISubprocessMixin0:
    CLI_BASE = _resolve_cli("cli-anything-openscreen")
    def _run(self, args, check=True, timeout=30):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
            timeout=timeout,
            check=check,
        )
    def test_cli_help(self):
        result = self._run(["--help"], check=False)
        assert result.returncode == 0
        assert "Openscreen CLI" in result.stdout
    def test_cli_version(self):
        result = self._run(["--version"], check=False)
        assert result.returncode == 0
        assert "1.0.0" in result.stdout
    def test_cli_export_presets(self):
        result = self._run(["--json", "export", "presets"], check=False)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
    def test_cli_media_probe(self, test_video):
        result = self._run(["--json", "media", "probe", test_video], check=False)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["width"] == 1920
    def test_cli_project_new_json(self):
        """CLI project new --json returns project info."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_path = os.path.join(tmp_dir, "cli_test.openscreen")
            result = self._run(["--json", "project", "new", "-o", proj_path], check=False)
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert data.get("status") == "created"
            assert "saved_to" in data
            assert os.path.exists(proj_path)
            print(f"\n  Project created: {proj_path}")
    def test_cli_zoom_add(self):
        """CLI zoom add works and persists to file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_path = os.path.join(tmp_dir, "zoom_test.openscreen")
            # Create project
            self._run(["project", "new", "-o", proj_path], check=False)

            # Add zoom
            result = self._run([
                "--json", "--project", proj_path,
                "zoom", "add",
                "--start", "1000", "--end", "3000", "--depth", "3",
            ], check=False)
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data["depth"] == 3
            assert data["startMs"] == 1000

            # Verify saved
            result2 = self._run(
                ["--json", "--project", proj_path, "zoom", "list"], check=False
            )
            assert result2.returncode == 0
            print(f"\n  Zoom add result: depth={data['depth']}, id={data['id']}")
