# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, tmp_dir  # noqa: F401,E501


class _TestCLISubprocessMixin2:
    def test_cloud_mesh_delaunay_workflow(self, tmp_dir, cloud_xyz):
        """Workflow: add cloud → mesh-delaunay → verify mesh."""
        proj_path = os.path.join(tmp_dir, "delaunay_wf.json")
        mesh_out = os.path.join(tmp_dir, "terrain.obj")

        self._run(["project", "new", "-o", proj_path])
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz])

        result = self._run([
            "--json", "--project", proj_path,
            "cloud", "mesh-delaunay", "0", "-o", mesh_out,
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("exists"), f"mesh-delaunay produced no output: {result.stderr[:300]}"
        assert data["file_size"] > 0
        print(f"\n  Delaunay mesh: {mesh_out} ({data['file_size']:,} bytes)")
    def test_transform_apply_workflow(self, tmp_dir, cloud_xyz):
        """Workflow: add cloud → apply identity transform → verify output."""
        proj_path = os.path.join(tmp_dir, "trans_wf.json")
        mat_file = os.path.join(tmp_dir, "identity.txt")
        out_cloud = os.path.join(tmp_dir, "transformed.xyz")

        with open(mat_file, "w") as f:
            f.write("1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n")

        self._run(["project", "new", "-o", proj_path])
        self._run(["--project", proj_path, "cloud", "add", cloud_xyz])

        result = self._run([
            "--json", "--project", proj_path,
            "transform", "apply", "0",
            "-o", out_cloud, "-m", mat_file,
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("exists"), f"transform apply produced no output: {result.stderr[:300]}"
        print(f"\n  Transformed: {out_cloud} ({data['file_size']:,} bytes)")
