# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import repo_root, runner  # noqa: F401,E501


class _TestCLIMixin1:
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_setup_node_auto_with_client_selection_uses_phase2(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        backend.run_wrapper.return_value = {
            "command": ["phase2", "--execution=geth", "--consensus=lighthouse"],
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
                "setup-node",
                "--network",
                "holesky",
                "--execution-client",
                "geth",
                "--consensus-client",
                "lighthouse",
                "--confirm",
            ],
        )
        assert result.exit_code == 0
        backend.run_wrapper.assert_called_once_with(
            "phase2",
            "--execution=geth",
            "--consensus=lighthouse",
        )
        payload = json.loads(result.output)
        assert payload["requested_phase"] == "auto-phase2"
        assert payload["requested"]["network"] == "holesky"
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_start_rpc_requires_confirm(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "start-rpc",
                "--web-stack",
                "nginx",
            ],
        )
        assert result.exit_code == 1
        assert "requires --confirm" in result.output
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_configure_validator_json(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "--json",
                "configure-validator",
                "--consensus-client",
                "prysm",
                "--fee-recipient",
                "0x1111111111111111111111111111111111111111",
                "--graffiti",
                "test",
            ],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["plan"]["consensus_client"] == "prysm"
        assert payload["plan"]["config_updates"]["GRAFITTI"] == "test"
    def test_configure_validator_rejects_unknown_consensus_client(
        self, runner: CliRunner, repo_root: Path
    ):
        result = runner.invoke(
            cli,
            [
                "--repo-root",
                str(repo_root),
                "configure-validator",
                "--consensus-client",
                "bad-client",
            ],
        )
        assert result.exit_code == 2
        assert "Invalid value for '--consensus-client'" in result.output
