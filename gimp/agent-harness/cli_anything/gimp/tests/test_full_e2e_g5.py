# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestGIMPBackend:
    """Tests that verify GIMP is installed and accessible."""

    def test_gimp_is_installed(self):
        from cli_anything.gimp.utils.gimp_backend import find_gimp

        path = find_gimp()
        assert os.path.exists(path)
        print(f"\n  GIMP binary: {path}")

    def test_gimp_version(self):
        from cli_anything.gimp.utils.gimp_backend import get_version

        version = get_version()
        assert "image manipulation" in version.lower() or "gimp" in version.lower()
        print(f"\n  GIMP version: {version}")


class TestGIMPRenderE2E:
    """True E2E tests using GIMP batch mode."""

    def test_create_and_export_png(self):
        """Create a blank image in GIMP and export as PNG."""
        from cli_anything.gimp.utils.gimp_backend import create_and_export

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "test.png")
            result = create_and_export(200, 150, output, fill_color="red", timeout=60)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            assert result["method"] == "gimp-batch"
            print(f"\n  GIMP PNG: {result['output']} ({result['file_size']:,} bytes)")

    def test_create_and_export_jpeg(self):
        """Create a blank image in GIMP and export as JPEG."""
        from cli_anything.gimp.utils.gimp_backend import create_and_export

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "test.jpg")
            result = create_and_export(200, 150, output, fill_color="blue", timeout=60)

            assert os.path.exists(result["output"])
            assert result["file_size"] > 0
            print(f"\n  GIMP JPEG: {result['output']} ({result['file_size']:,} bytes)")
