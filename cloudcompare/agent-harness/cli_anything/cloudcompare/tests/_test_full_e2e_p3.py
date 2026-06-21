# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import cloud_xyz, tmp_dir  # noqa: F401,E501


class TestSFColorOps:
    """Tests for scalar-field ↔ RGB colour conversion."""

    @pytest.fixture
    def cloud_with_sf(self, tmp_dir, cloud_xyz):
        """Cloud with Z as active scalar field (PLY preserves SF)."""
        from cli_anything.cloudcompare.utils.cc_backend import coord_to_sf
        out = os.path.join(tmp_dir, "cloud_sf.ply")
        result = coord_to_sf(cloud_xyz, out, dimension="Z")
        assert result["returncode"] == 0, result["stderr"][:300]
        return out

    def test_sf_to_rgb(self, tmp_dir, cloud_with_sf):
        from cli_anything.cloudcompare.utils.cc_backend import sf_to_rgb
        out = os.path.join(tmp_dir, "cloud_rgb.ply")
        result = sf_to_rgb(cloud_with_sf, out)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "sf_to_rgb produced no output"
        assert result["file_size"] > 0
        print(f"\n  SF→RGB: {out} ({result['file_size']:,} bytes)")

    def test_rgb_to_sf(self, tmp_dir, cloud_with_sf):
        """Round-trip: SF→RGB then RGB→SF."""
        from cli_anything.cloudcompare.utils.cc_backend import sf_to_rgb, rgb_to_sf
        rgb_out = os.path.join(tmp_dir, "cloud_rgb2.ply")
        sf_out  = os.path.join(tmp_dir, "cloud_sf2.ply")
        r1 = sf_to_rgb(cloud_with_sf, rgb_out)
        assert r1["returncode"] == 0
        r2 = rgb_to_sf(rgb_out, sf_out)
        assert r2["returncode"] == 0, r2["stderr"][:300]
        assert r2.get("exists"), "rgb_to_sf produced no output"
        print(f"\n  RGB→SF: {sf_out} ({r2['file_size']:,} bytes)")


class TestNoisePCLFilter:
    """Tests for the PCL noise filter (-NOISE KNN/RADIUS REL/ABS).

    Note: CloudCompare's CLI does not expose Gaussian/Bilateral spatial
    smoothing. The -NOISE command (PCL wrapper plugin) is the closest
    equivalent for noise removal available via the command line.
    """

    def test_noise_filter_knn(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter
        out = os.path.join(tmp_dir, "denoised_knn.xyz")
        result = noise_filter(cloud_xyz, out, knn=6, noisiness=1.0)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "noise_filter (KNN) produced no output"
        assert result["file_size"] > 0
        print(f"\n  Noise(KNN): {out} ({result['file_size']:,} bytes)")

    def test_noise_filter_radius(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter
        out = os.path.join(tmp_dir, "denoised_radius.xyz")
        result = noise_filter(cloud_xyz, out, use_radius=True, radius=0.2, noisiness=1.0)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "noise_filter (RADIUS) produced no output"
        print(f"\n  Noise(RADIUS): {out} ({result['file_size']:,} bytes)")

    def test_noise_filter_absolute(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import noise_filter
        out = os.path.join(tmp_dir, "denoised_abs.xyz")
        result = noise_filter(cloud_xyz, out, knn=6, noisiness=0.05, absolute=True)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "noise_filter (ABS) produced no output"
        print(f"\n  Noise(ABS): {out} ({result['file_size']:,} bytes)")


class TestNormalsOps:
    """Tests for normal computation and inversion."""

    def test_invert_normals(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import compute_normals, invert_normals
        with_normals = os.path.join(tmp_dir, "normals.ply")
        inverted = os.path.join(tmp_dir, "normals_inv.ply")
        r1 = compute_normals(cloud_xyz, with_normals, octree_level=8)
        assert r1["returncode"] == 0, r1["stderr"][:300]
        r2 = invert_normals(with_normals, inverted)
        assert r2["returncode"] == 0, r2["stderr"][:300]
        assert r2.get("exists"), "invert_normals produced no output"
        print(f"\n  Inverted normals: {inverted} ({r2['file_size']:,} bytes)")


class TestDelaunayMesh:
    """Tests for Delaunay 2.5-D mesh generation and mesh sampling."""

    def test_delaunay_creates_mesh(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import delaunay_mesh
        out = os.path.join(tmp_dir, "terrain.obj")
        result = delaunay_mesh(cloud_xyz, out, axis_aligned=True)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "delaunay_mesh produced no output"
        assert result["file_size"] > 0
        print(f"\n  Delaunay mesh: {out} ({result['file_size']:,} bytes)")

    def test_delaunay_best_fit(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import delaunay_mesh
        out = os.path.join(tmp_dir, "terrain_bf.obj")
        result = delaunay_mesh(cloud_xyz, out, axis_aligned=False)
        assert result["returncode"] == 0, result["stderr"][:300]
        assert result.get("exists"), "delaunay best-fit produced no output"

    def test_sample_mesh(self, tmp_dir, cloud_xyz):
        from cli_anything.cloudcompare.utils.cc_backend import delaunay_mesh, sample_mesh
        mesh_out   = os.path.join(tmp_dir, "terrain.obj")
        sample_out = os.path.join(tmp_dir, "sampled.xyz")
        r1 = delaunay_mesh(cloud_xyz, mesh_out)
        assert r1["returncode"] == 0, r1["stderr"][:300]
        r2 = sample_mesh(mesh_out, sample_out, count=500)
        assert r2["returncode"] == 0, r2["stderr"][:300]
        assert r2.get("exists"), "sample_mesh produced no output"
        print(f"\n  Sampled {500} pts → {sample_out} ({r2['file_size']:,} bytes)")
