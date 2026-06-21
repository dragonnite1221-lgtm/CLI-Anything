# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


@pytest.mark.skipif(not _sbox_available(), reason="s&box not installed (set SBOX_PATH or install via Steam)")
class TestE2EBackend:
    """Tests that invoke real s&box backend executables.

    These tests require s&box to be installed. They verify the CLI
    can find and invoke the real software.
    """

    def test_find_sbox_installation(self):
        """Verify s&box installation is found."""
        import platform
        from cli_anything.sbox.utils.sbox_backend import find_sbox_installation

        sbox_path = find_sbox_installation()
        assert os.path.isdir(sbox_path)
        binary_name = "sbox-dev.exe" if platform.system() == "Windows" else "sbox-dev"
        assert os.path.isfile(os.path.join(sbox_path, binary_name))
        print(f"\n  s&box: {sbox_path}")

    def test_get_sbox_version(self):
        """Read s&box version info."""
        from cli_anything.sbox.utils.sbox_backend import get_sbox_version

        version = get_sbox_version()
        assert "version" in version
        print(f"\n  Version: {version}")

    def test_find_server_executable(self):
        """Find sbox-server.exe."""
        from cli_anything.sbox.utils.sbox_backend import find_executable

        path = find_executable("sbox-server")
        assert os.path.isfile(path)
        print(f"\n  Server: {path}")
