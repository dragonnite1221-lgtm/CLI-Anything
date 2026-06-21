# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _resolve_cli, project_json, tmp_dir  # noqa: F401,E501


class TestCSFFilter:
    """E2E tests for the Cloth Simulation Filter (CSF) ground extraction."""

    @pytest.fixture
    def scene_cloud(self, tmp_dir):
        """Synthetic scene: 100 ground points (z≈0) + 25 elevated points (z=5)."""
        path = os.path.join(tmp_dir, "scene.xyz")
        with open(path, "w") as f:
            for i in range(10):
                for j in range(10):
                    f.write(f"{i * 0.5:.1f} {j * 0.5:.1f} 0.0\n")
            for i in range(5):
                for j in range(5):
                    f.write(f"{i * 0.5:.1f} {j * 0.5:.1f} 5.0\n")
        return path

    def test_csf_extracts_ground(self, tmp_dir, scene_cloud):
        """CSF filter produces a ground cloud."""
        from cli_anything.cloudcompare.utils.cc_backend import csf_filter

        ground_out = os.path.join(tmp_dir, "ground.las")
        result = csf_filter(scene_cloud, ground_out, scene="FLAT",
                            cloth_resolution=0.5, class_threshold=0.3)

        assert result["returncode"] == 0, f"CSF failed:\n{result['stderr'][:400]}"
        assert result["ground_exists"], "Ground cloud not created"
        assert result["ground_size"] > 0
        print(f"\n  CSF ground: {ground_out} ({result['ground_size']:,} bytes)")

    def test_csf_exports_both_layers(self, tmp_dir, scene_cloud):
        """CSF filter exports both ground and off-ground clouds."""
        from cli_anything.cloudcompare.utils.cc_backend import csf_filter

        ground_out    = os.path.join(tmp_dir, "ground.las")
        offground_out = os.path.join(tmp_dir, "offground.las")
        result = csf_filter(scene_cloud, ground_out, offground_out,
                            scene="FLAT", cloth_resolution=0.5, class_threshold=0.3)

        assert result["returncode"] == 0
        assert result["ground_exists"]
        assert result["offground_exists"]
        assert result["ground_size"] > 0
        assert result["offground_size"] > 0

        # Ground + offground must account for all input points
        def _las_point_count(p):
            """Read POINTS count from a LAS/PCD/ASC file (best-effort)."""
            import struct
            with open(p, "rb") as f:
                header = f.read(375)
            # LAS 1.x: point count at offset 107 (uint32)
            try:
                return struct.unpack_from("<I", header, 107)[0]
            except Exception:
                return None

        g = _las_point_count(ground_out)
        u = _las_point_count(offground_out)
        if g is not None and u is not None:
            assert g + u == 125, f"Point count mismatch: {g} + {u} != 125"
        print(f"\n  Ground: {result['ground_size']:,} B  Off-ground: {result['offground_size']:,} B")

    def test_csf_cli_command(self, tmp_dir, project_json, scene_cloud):
        """cloud filter-csf via installed CLI subprocess."""
        cli = _resolve_cli("cli-anything-cloudcompare")
        ground_out = os.path.join(tmp_dir, "ground.las")

        subprocess.run(cli + ["project", "new", "-o", project_json],
                       capture_output=True, check=True)
        subprocess.run(cli + ["--project", project_json, "cloud", "add", scene_cloud],
                       capture_output=True, check=True)

        r = subprocess.run(
            cli + [
                "--json", "--project", project_json,
                "cloud", "filter-csf", "0",
                "--ground", ground_out,
                "--scene", "FLAT",
                "--cloth-resolution", "0.5",
                "--class-threshold", "0.3",
            ],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"CLI CSF failed:\nstdout={r.stdout}\nstderr={r.stderr}"
        data = json.loads(r.stdout)
        assert data["ground_exists"]
        assert data["ground_size"] > 0
        print(f"\n  CLI CSF → {data['ground_size']:,} bytes")
