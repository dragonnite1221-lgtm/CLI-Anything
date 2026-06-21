# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


def _resolve_cli(name: str) -> list[str]:
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"\n[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = "cli_anything.cloudcompare.cloudcompare_cli"
    print(f"\n[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


def _make_xyz_cloud(path: str, n_points: int = 200, add_noise: bool = False) -> str:
    """Generate a synthetic XYZ cloud file.

    Creates points on a flat plane (z=0) with optional outlier noise.
    Format: x y z (space separated, no header) — CloudCompare ASC format.
    """
    import math
    import random
    random.seed(42)

    grid = int(math.sqrt(n_points))
    with open(path, "w") as f:
        for i in range(grid):
            for j in range(grid):
                x = i * 0.1
                y = j * 0.1
                z = 0.0 + random.uniform(-0.001, 0.001)  # nearly flat
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")

        if add_noise:
            # Add outlier points far from the plane
            for _ in range(10):
                x = random.uniform(0, 1)
                y = random.uniform(0, 1)
                z = random.uniform(10, 20)  # way above the plane
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
    return path


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def cloud_xyz(tmp_dir):
    """A small synthetic point cloud (XYZ format)."""
    path = os.path.join(tmp_dir, "cloud.xyz")
    _make_xyz_cloud(path, n_points=225)
    print(f"\n  Input cloud: {path}")
    return path


@pytest.fixture
def noisy_cloud_xyz(tmp_dir):
    """A cloud with outlier noise points."""
    path = os.path.join(tmp_dir, "noisy_cloud.xyz")
    _make_xyz_cloud(path, n_points=100, add_noise=True)
    return path


@pytest.fixture
def project_json(tmp_dir):
    return os.path.join(tmp_dir, "test.json")


class TestBackendAvailability:
    def test_cloudcompare_is_installed(self):
        """CloudCompare MUST be installed — this test will fail if not."""
        from cli_anything.cloudcompare.utils.cc_backend import find_cloudcompare, is_available
        assert is_available(), (
            "CloudCompare is not installed!\n"
            "Install with: flatpak install flathub org.cloudcompare.CloudCompare"
        )
        cmd = find_cloudcompare()
        assert len(cmd) > 0
        print(f"\n  CloudCompare command: {' '.join(cmd)}")


class TestFormatConversion:
    def test_xyz_to_ply(self, tmp_dir, cloud_xyz):
        """Convert XYZ cloud to PLY format via CloudCompare."""
        from cli_anything.cloudcompare.utils.cc_backend import convert_format

        output_path = os.path.join(tmp_dir, "output.ply")
        result = convert_format(cloud_xyz, output_path)

        assert result["returncode"] == 0, (
            f"CloudCompare failed (exit {result['returncode']}):\n{result['stderr'][:800]}"
        )
        assert result.get("exists"), f"Output PLY not created: {output_path}"
        assert result["file_size"] > 0, "Output PLY is empty"

        # Verify PLY magic bytes
        with open(output_path, "rb") as f:
            header = f.read(10)
        assert header.startswith(b"ply"), f"Output is not a valid PLY file: {header[:10]}"

        print(f"\n  PLY output: {output_path} ({result['file_size']:,} bytes)")

    def test_xyz_to_las(self, tmp_dir, cloud_xyz):
        """Convert XYZ cloud to LAS format via CloudCompare."""
        from cli_anything.cloudcompare.utils.cc_backend import convert_format

        output_path = os.path.join(tmp_dir, "output.las")
        result = convert_format(cloud_xyz, output_path)

        assert result["returncode"] == 0, (
            f"CloudCompare failed:\n{result['stderr'][:800]}"
        )
        assert result.get("exists"), f"Output LAS not created: {output_path}"
        assert result["file_size"] > 0

        # Verify LAS magic bytes ("LASF")
        with open(output_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"LASF", f"Output is not a valid LAS file: {magic}"

        print(f"\n  LAS output: {output_path} ({result['file_size']:,} bytes)")
