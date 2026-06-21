# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import repo_root, runner  # noqa: F401,E501


class _TestCLIMixin0:
    def test_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "setup-node" in result.output
        assert "health-check" in result.output
    def test_missing_repo_root_returns_clean_json_error(self, runner: CliRunner):
        result = runner.invoke(cli, ["--json", "health-check"])
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert "Could not locate an eth2-quickstart checkout" in payload["error"]
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_health_check_json(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        backend.run_wrapper.return_value = {
            "command": ["doctor", "--json"],
            "cwd": str(repo_root),
            "exit_code": 0,
            "stdout": json.dumps({"summary": {"status": "pass"}}),
            "stderr": "",
            "ok": True,
        }
        result = runner.invoke(
            cli,
            ["--repo-root", str(repo_root), "--json", "health-check"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["doctor"]["summary"]["status"] == "pass"
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_install_clients_json(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        backend.run_wrapper.return_value = {
            "command": ["phase2"],
            "cwd": str(repo_root),
            "exit_code": 0,
            "stdout": "installed",
            "stderr": "",
            "ok": True,
        }
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "--json",
                "install-clients",
                "--network",
                "mainnet",
                "--execution-client",
                "geth",
                "--consensus-client",
                "lighthouse",
                "--mev",
                "mev-boost",
                "--confirm",
            ],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["requested"]["execution_client"] == "geth"
        assert payload["requested"]["consensus_client"] == "lighthouse"
    def test_install_clients_rejects_unknown_execution_client(self, runner: CliRunner, repo_root: Path):
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "install-clients",
                "--execution-client",
                "bad-client",
                "--consensus-client",
                "lighthouse",
                "--confirm",
            ],
        )
        assert result.exit_code == 2
        assert "Invalid value for '--execution-client'" in result.output
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_setup_node_auto_with_network_only_uses_ensure(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        backend.run_wrapper.return_value = {
            "command": ["ensure", "--apply", "--confirm"],
            "cwd": str(repo_root),
            "exit_code": 0,
            "stdout": "ensured",
            "stderr": "",
            "ok": True,
        }
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "--json",
                "setup-node",
                "--network",
                "holesky",
                "--confirm",
            ],
        )
        assert result.exit_code == 0
        backend.run_wrapper.assert_called_once_with("ensure", "--apply", "--confirm")
        payload = json.loads(result.output)
        assert payload["requested_phase"] == "auto-ensure"
        assert payload["requested"]["network"] == "holesky"
        assert payload["config_path"] is not None
