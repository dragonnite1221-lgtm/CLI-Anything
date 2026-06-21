# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, tmp_dir  # noqa: F401,E501


class _TestCLISubprocessMixin1:
    def test_full_subsample_workflow(self, tmp_dir, cloud_xyz):
        """Full workflow: create project → add cloud → subsample → verify output."""
        proj_path = os.path.join(tmp_dir, "subsample_wf.json")
        out_cloud = os.path.join(tmp_dir, "subsampled.las")

        # Create project
        self._run(["project", "new", "-o", proj_path])

        # Add cloud
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz])

        # Subsample via CloudCompare
        result = self._run([
            "--json", "--project", proj_path,
            "cloud", "subsample", "0",
            "-o", out_cloud,
            "--method", "SPATIAL",
            "--param", "0.15",
            "--add-to-project",
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)

        assert data.get("exists") is True, (
            f"CloudCompare did not produce output.\n"
            f"Result: {json.dumps(data, indent=2)}"
        )
        assert os.path.exists(data["output"]), f"Output file missing: {data['output']}"

        # Verify LAS magic bytes
        with open(data["output"], "rb") as f:
            magic = f.read(4)
        assert magic == b"LASF", f"Output is not valid LAS: {magic}"

        print(f"\n  Subsampled cloud: {data['output']}")
        print(f"  File size: {data.get('file_size', '?'):,} bytes")

        # Verify project was updated (--add-to-project)
        info_result = self._run(["--json", "--project", proj_path, "project", "info"])
        info = json.loads(info_result.stdout)
        assert info["cloud_count"] == 2
    def test_full_export_workflow(self, tmp_dir, cloud_xyz):
        """Full workflow: create project → add cloud → export to PLY."""
        proj_path = os.path.join(tmp_dir, "export_wf.json")
        out_cloud = os.path.join(tmp_dir, "exported.ply")

        self._run(["project", "new", "-o", proj_path])
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz])
        result = self._run([
            "--json", "--project", proj_path,
            "export", "cloud", "0", out_cloud,
            "--overwrite",
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)

        assert os.path.exists(data["output"]), f"Exported PLY missing: {data['output']}"
        assert data["file_size"] > 0

        with open(data["output"], "rb") as f:
            assert f.read(3) == b"ply"

        print(f"\n  Exported PLY: {data['output']} ({data['file_size']:,} bytes)")
    def test_project_status_json(self, tmp_dir):
        """project status --json returns quick status."""
        proj_path = os.path.join(tmp_dir, "status_test.json")
        self._run(["project", "new", "-o", proj_path])
        result = self._run(["--json", "--project", proj_path, "project", "status"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "clouds" in data
        assert "meshes" in data
        assert "modified" in data
    def test_cloud_invert_normals_workflow(self, tmp_dir, cloud_xyz):
        """Workflow: add cloud → normals → invert-normals."""
        proj_path = os.path.join(tmp_dir, "normals_wf.json")
        normals_out = os.path.join(tmp_dir, "normals.ply")
        inv_out = os.path.join(tmp_dir, "normals_inv.ply")

        self._run(["project", "new", "-o", proj_path])
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz])

        # Compute normals
        r1 = self._run([
            "--json", "--project", proj_path,
            "cloud", "normals", "0", "-o", normals_out, "--add-to-project",
        ])
        assert r1.returncode == 0
        d1 = json.loads(r1.stdout)
        assert d1.get("exists"), "normals command produced no output"

        # Add normals cloud and invert
        r2 = self._run([
            "--json", "--project", proj_path,
            "cloud", "invert-normals", "1", "-o", inv_out,
        ])
        assert r2.returncode == 0
        d2 = json.loads(r2.stdout)
        assert d2.get("exists"), "invert-normals produced no output"
        print(f"\n  Inverted normals: {inv_out} ({d2['file_size']:,} bytes)")
