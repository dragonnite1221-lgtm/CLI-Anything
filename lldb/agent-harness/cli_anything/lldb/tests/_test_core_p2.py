# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-lldb")

    def _run(self, args, check=True):
        harness_root = str(Path(__file__).resolve().parents[3])
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            cwd=harness_root,
        )

    def test_cli_help_subprocess(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "LLDB CLI" in result.stdout
