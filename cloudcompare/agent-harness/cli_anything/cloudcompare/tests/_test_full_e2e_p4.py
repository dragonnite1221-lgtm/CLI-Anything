# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, tmp_dir  # noqa: F401,E501


class TestApplyTransform:
    """Tests for -APPLY_TRANS (rigid-body transformation)."""

    def test_apply_identity_matrix(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import apply_transform
        mat_file = os.path.join(tmp_dir, "identity.txt")
        with open(mat_file, "w") as f:
            f.write("1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n")
        out = os.path.join(tmp_dir, "transformed.xyz")
        result = apply_transform(cloud_xyz, out, mat_file)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "apply_transform produced no output"
        print(f"\n  Transformed cloud: {out} ({result['file_size']:,} bytes)")

    def test_apply_translation_matrix(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import apply_transform
        mat_file = os.path.join(tmp_dir, "translate.txt")
        with open(mat_file, "w") as f:
            f.write("1 0 0 5\n0 1 0 0\n0 0 1 0\n0 0 0 1\n")  # translate X by 5
        out = os.path.join(tmp_dir, "translated.xyz")
        result = apply_transform(cloud_xyz, out, mat_file)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "Translation transform produced no output"


class TestSegmentCC:
    """Tests for connected-component segmentation (EXTRACT_CC)."""

    @pytest.fixture
    def two_cluster_cloud(self, tmp_dir):
        """Two spatially separated clusters of 50 points each."""
        import random
        random.seed(7)
        path = os.path.join(tmp_dir, "two_clusters.xyz")
        with open(path, "w") as f:
            # Cluster A near origin
            for _ in range(50):
                x = random.uniform(0.0, 0.1)
                y = random.uniform(0.0, 0.1)
                z = random.uniform(0.0, 0.1)
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
            # Cluster B far away
            for _ in range(50):
                x = random.uniform(10.0, 10.1)
                y = random.uniform(10.0, 10.1)
                z = random.uniform(10.0, 10.1)
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
        return path

    def test_extract_two_components(self, tmp_dir, two_cluster_cloud):
        from cli_anything.cloudcompare.utils.cc_backend import extract_connected_components
        out_dir = os.path.join(tmp_dir, "components")
        result = extract_connected_components(
            two_cluster_cloud, out_dir,
            octree_level=8, min_points=10, output_fmt="xyz",
        )
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result["component_count"] >= 2, (
            f"Expected ≥2 components, got {result['component_count']}.\n"
            f"Components: {result['components']}"
        )
        print(f"\n  CC segments: {result['component_count']} components in {out_dir}")
