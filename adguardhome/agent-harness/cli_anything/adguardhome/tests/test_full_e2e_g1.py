# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestDockerE2E:
    CLI_BASE = _resolve_cli("cli-anything-adguardhome")

    def _run_agh(
        self, args: list[str], agh: dict, check: bool = True
    ) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["AGH_HOST"] = agh["host"]
        env["AGH_PORT"] = str(agh["port"])
        env["AGH_USERNAME"] = agh["username"]
        env["AGH_PASSWORD"] = agh["password"]
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            env=env,
        )

    def test_server_status_json(self, agh_docker):
        result = self._run_agh(["--json", "server", "status"], agh_docker)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        print(f"\n  Server status: {data}")
        assert isinstance(data, dict)

    def test_filter_list_json(self, agh_docker):
        result = self._run_agh(["--json", "filter", "list"], agh_docker)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        print(f"\n  Filters: {data}")
        assert "filters" in data or isinstance(data, dict)

    def test_rewrite_lifecycle(self, agh_docker):
        """Add rewrite, verify in list, remove, verify gone."""
        # Add
        add_result = self._run_agh(
            [
                "--json",
                "rewrite",
                "add",
                "--domain",
                "test-cli.local",
                "--answer",
                "10.0.0.99",
            ],
            agh_docker,
        )
        assert add_result.returncode == 0
        print(f"\n  Rewrite add: {add_result.stdout.strip()}")

        # List and verify
        list_result = self._run_agh(["--json", "rewrite", "list"], agh_docker)
        assert list_result.returncode == 0
        rewrites = json.loads(list_result.stdout)
        print(f"\n  Rewrites: {rewrites}")
        domains = [
            r.get("domain") for r in (rewrites if isinstance(rewrites, list) else [])
        ]
        assert "test-cli.local" in domains

        # Remove
        rm_result = self._run_agh(
            [
                "--json",
                "rewrite",
                "remove",
                "--domain",
                "test-cli.local",
                "--answer",
                "10.0.0.99",
            ],
            agh_docker,
        )
        assert rm_result.returncode == 0

        # Verify removed
        list_result2 = self._run_agh(["--json", "rewrite", "list"], agh_docker)
        rewrites2 = json.loads(list_result2.stdout)
        domains2 = [
            r.get("domain") for r in (rewrites2 if isinstance(rewrites2, list) else [])
        ]
        assert "test-cli.local" not in domains2
        print(f"\n  Rewrite lifecycle: PASS")

    def test_stats_show_json(self, agh_docker):
        result = self._run_agh(["--json", "stats", "show"], agh_docker)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        print(
            f"\n  Stats keys: {list(data.keys()) if isinstance(data, dict) else 'list'}"
        )
        assert isinstance(data, dict)

    def test_config_test(self, agh_docker):
        result = self._run_agh(["--json", "config", "test"], agh_docker)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        print(f"\n  Config test: {data}")
        assert data.get("connected") is True
