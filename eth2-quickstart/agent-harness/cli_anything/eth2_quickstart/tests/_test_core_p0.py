# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    repo = tmp_path / "eth2-quickstart"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "eth2qs.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    (repo / "config").mkdir()
    return repo


class TestProjectHelpers:
    def test_find_repo_root_from_explicit_path(self, repo_root: Path):
        resolved = project.find_repo_root(str(repo_root))
        assert resolved == repo_root

    def test_find_repo_root_from_env(self, repo_root: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("ETH2QS_REPO_ROOT", str(repo_root))
        resolved = project.find_repo_root()
        assert resolved == repo_root

    def test_upsert_user_config(self, repo_root: Path):
        config_path = project.upsert_user_config(
            repo_root,
            {
                "ETH_NETWORK": "holesky",
                "EXEC_CLIENT": "geth",
            },
        )
        content = config_path.read_text(encoding="utf-8")
        assert "export ETH_NETWORK='holesky'" in content
        assert "export EXEC_CLIENT='geth'" in content

        project.upsert_user_config(repo_root, {"ETH_NETWORK": "mainnet"})
        updated = config_path.read_text(encoding="utf-8")
        assert "export ETH_NETWORK='mainnet'" in updated
        assert "export ETH_NETWORK='holesky'" not in updated


class TestValidatorPlan:
    def test_prysm_plan(self):
        plan = validator_plan(
            consensus_client="prysm",
            fee_recipient="0xabc",
            graffiti="hello",
            wallet_password_file="~/secrets/pass.txt",
        )
        assert plan["config_updates"]["FEE_RECIPIENT"] == "0xabc"
        assert "validator accounts import" in plan["import_command"]
        assert "wallet-password-file" in plan["post_import_commands"][0]

    def test_invalid_client(self):
        with pytest.raises(ValueError, match="Unsupported consensus client"):
            validator_plan(consensus_client="bad-client")


class TestBackendErrors:
    def test_run_handles_missing_wrapper(self, repo_root: Path):
        from cli_anything.eth2_quickstart.utils.eth2qs_backend import Eth2QuickStartBackend

        backend = Eth2QuickStartBackend(str(repo_root))
        result = backend._run(["/definitely/missing/eth2qs.sh"])
        assert result["ok"] is False
        assert result["exit_code"] == 127
        assert "command not found" in result["stderr"]

    @patch("cli_anything.eth2_quickstart.utils.eth2qs_backend.subprocess.run")
    def test_run_handles_permission_error(self, run_mock, repo_root: Path):
        from cli_anything.eth2_quickstart.utils.eth2qs_backend import Eth2QuickStartBackend

        run_mock.side_effect = PermissionError("no execute bit")
        backend = Eth2QuickStartBackend(str(repo_root))
        result = backend._run(["/tmp/not-executable"])
        assert result["ok"] is False
        assert result["exit_code"] == 126
        assert "permission denied" in result["stderr"]
