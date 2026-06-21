# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@skip_no_lldb
class TestCoreE2E:
    def test_core_load_requires_target(self, session_file: Path, core_file: str):
        cmd = [
            sys.executable,
            "-m",
            "cli_anything.lldb.lldb_cli",
            "--json",
            "--session-file",
            str(session_file),
            "core",
            "load",
            "--path",
            core_file,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=HARNESS_ROOT)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "error" in data
