# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-adguardhome")

    def _run(
        self, args: list[str], check: bool = True, env: dict | None = None
    ) -> subprocess.CompletedProcess:
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            env=run_env,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "adguardhome" in result.stdout.lower() or "Usage" in result.stdout

    def test_config_show_json(self):
        result = self._run(["--json", "config", "show"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "host" in data
        assert "port" in data

    def test_config_show_default_host(self):
        result = self._run(["--json", "config", "show"])
        data = json.loads(result.stdout)
        assert data["host"] == "localhost"
        assert data["port"] == 3000

    def test_help_subcommands_listed(self):
        result = self._run(["--help"])
        assert "filter" in result.stdout
        assert "server" in result.stdout
        assert "stats" in result.stdout

    def test_filter_help(self):
        result = self._run(["filter", "--help"])
        assert result.returncode == 0
        assert "list" in result.stdout

    def test_rewrite_help(self):
        result = self._run(["rewrite", "--help"])
        assert result.returncode == 0

    def test_blocking_help(self):
        result = self._run(["blocking", "--help"])
        assert result.returncode == 0
