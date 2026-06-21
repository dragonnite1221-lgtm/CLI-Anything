# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import test_video  # noqa: F401,E501


class _TestCLISubprocessMixin1:
    def test_cli_full_workflow(self, test_video):
        """Full CLI workflow: create project, add regions, export."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_path = os.path.join(tmp_dir, "workflow.openscreen")
            output_path = os.path.join(tmp_dir, "workflow_output.mp4")

            # 1. Create project with video
            result = self._run(
                ["project", "new", "-v", test_video, "-o", proj_path], check=False
            )
            assert result.returncode == 0
            assert os.path.exists(proj_path)

            # 2. Add zoom region
            result = self._run([
                "--project", proj_path,
                "zoom", "add",
                "--start", "1000", "--end", "2000", "--depth", "2",
            ], check=False)
            assert result.returncode == 0

            # 3. Set quality
            result = self._run([
                "--project", proj_path,
                "project", "set", "exportQuality", "medium",
            ], check=False)
            assert result.returncode == 0

            # 4. Export
            result = self._run([
                "--json", "--project", proj_path,
                "export", "render", output_path,
            ], check=False)
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert os.path.exists(output_path)
            assert data["file_size"] > 1000

            # 5. Probe output
            result = self._run(
                ["--json", "media", "probe", output_path], check=False
            )
            assert result.returncode == 0
            probe_data = json.loads(result.stdout)
            assert probe_data["width"] > 0
            assert probe_data["duration"] > 0

            print(f"\n  Full workflow output: {output_path}")
            print(f"    Size: {data['file_size']:,} bytes")
            print(f"    Duration: {data['duration']:.2f}s")
            print(f"    Dimensions: {probe_data['width']}x{probe_data['height']}")
    def test_cli_media_check_valid(self, test_video):
        """CLI media check returns valid=True for a real video."""
        result = self._run(["--json", "media", "check", test_video], check=False)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["valid"] is True
    def test_cli_session_status(self):
        """CLI session status works."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_path = os.path.join(tmp_dir, "status_test.openscreen")
            self._run(["project", "new", "-o", proj_path], check=False)

            result = self._run(
                ["--json", "--project", proj_path, "session", "status"], check=False
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "project_open" in data
            assert "undo_available" in data
