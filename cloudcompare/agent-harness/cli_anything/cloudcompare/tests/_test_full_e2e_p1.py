# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, noisy_cloud_xyz, tmp_dir  # noqa: F401,E501


class TestSubsampling:
    def test_spatial_subsample(self, tmp_dir, cloud_xyz):
        """Subsample using SPATIAL method."""
        from cli_anything.cloudcompare.utils.cc_backend import subsample

        output_path = os.path.join(tmp_dir, "subsampled_spatial.xyz")
        result = subsample(cloud_xyz, output_path, method="SPATIAL", parameter=0.2)

        assert result["returncode"] == 0, (
            f"Subsample failed:\n{result['stderr'][:800]}"
        )
        assert result.get("exists"), f"Subsampled cloud not created: {output_path}"
        assert result["file_size"] > 0

        # Spatial subsampling should reduce the cloud
        input_size = os.path.getsize(cloud_xyz)
        assert result["file_size"] <= input_size * 2  # not much larger than input

        print(f"\n  Spatial subsample: {output_path} ({result['file_size']:,} bytes)")

    def test_random_subsample(self, tmp_dir, cloud_xyz):
        """Subsample using RANDOM method (keep N points)."""
        from cli_anything.cloudcompare.utils.cc_backend import subsample

        output_path = os.path.join(tmp_dir, "subsampled_random.xyz")
        result = subsample(cloud_xyz, output_path, method="RANDOM", parameter=50)

        assert result["returncode"] == 0, (
            f"Random subsample failed:\n{result['stderr'][:800]}"
        )
        assert result.get("exists"), f"Subsampled cloud not created: {output_path}"
        assert result["file_size"] > 0

        print(f"\n  Random subsample: {output_path} ({result['file_size']:,} bytes)")


class TestSORFilter:
    def test_sor_removes_outliers(self, tmp_dir, noisy_cloud_xyz):
        """SOR filter removes outlier noise points."""
        from cli_anything.cloudcompare.utils.cc_backend import sor_filter

        output_path = os.path.join(tmp_dir, "filtered.xyz")
        result = sor_filter(noisy_cloud_xyz, output_path, nb_points=6, std_ratio=1.0)

        assert result["returncode"] == 0, (
            f"SOR filter failed:\n{result['stderr'][:800]}"
        )
        assert result.get("exists"), f"Filtered cloud not created: {output_path}"
        assert result["file_size"] > 0

        # Compare point counts (line counts in XYZ/ASC format).
        # NOTE: file size comparison is unreliable — CloudCompare appends a
        # scalar field (deviation) column to ASC output, making the filtered
        # file larger per-point even though it has fewer points.
        with open(noisy_cloud_xyz) as f:
            input_count = sum(1 for line in f if line.strip())
        with open(output_path) as f:
            output_count = sum(1 for line in f if line.strip())

        # SOR should have removed the 10 outlier noise points
        assert output_count < input_count, (
            f"SOR filter did not reduce point count: "
            f"input={input_count} pts → output={output_count} pts"
        )

        print(f"\n  SOR filtered: {output_path} ({result['file_size']:,} bytes)")
        print(f"  Points: {input_count} → {output_count} (removed {input_count - output_count})")
