# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p3 import _resolve_cli  # noqa: F401,E501


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-audacity")

    def _run_cli(self, args, cwd=None):
        """Run the CLI as a subprocess."""
        result = subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
        )
        return result

    def test_cli_project_new(self):
        result = self._run_cli(["project", "new", "--name", "TestCLI"])
        assert result.returncode == 0
        assert "TestCLI" in result.stdout

    def test_cli_project_new_json(self):
        result = self._run_cli(["--json", "project", "new", "--name", "JsonTest"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["name"] == "JsonTest"

    def test_cli_effect_list_available(self):
        result = self._run_cli(["effect", "list-available"])
        assert result.returncode == 0
        assert "amplify" in result.stdout or "normalize" in result.stdout

    def test_cli_export_presets(self):
        result = self._run_cli(["export", "presets"])
        assert result.returncode == 0
        assert "wav" in result.stdout.lower()


class TestSoXBackend:
    """Tests that verify SoX is installed and accessible."""

    def test_sox_is_installed(self):
        from cli_anything.audacity.utils.sox_backend import find_sox
        path = find_sox()
        assert os.path.exists(path)
        print(f"\n  SoX binary: {path}")

    def test_sox_version(self):
        from cli_anything.audacity.utils.sox_backend import get_version
        version = get_version()
        assert version  # non-empty
        print(f"\n  SoX version: {version}")
