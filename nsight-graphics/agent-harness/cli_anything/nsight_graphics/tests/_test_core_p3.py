# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCLISubprocess:
    def test_cli_help_subprocess(self):
        harness_root = Path(__file__).resolve().parents[3]
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.nsight_graphics.nsight_graphics_cli", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(harness_root),
        )
        assert result.returncode == 0
        assert "Nsight Graphics CLI" in result.stdout
