# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import repo_root, runner  # noqa: F401,E501


class _TestCLIMixin2:
    @patch("cli_anything.eth2_quickstart.eth2_quickstart_cli.Eth2QuickStartBackend")
    def test_status_json(self, backend_cls, runner: CliRunner, repo_root: Path):
        backend = backend_cls.return_value
        backend.repo_root = repo_root
        backend.run_wrapper.side_effect = [
            {
                "command": ["doctor", "--json"],
                "cwd": str(repo_root),
                "exit_code": 0,
                "stdout": json.dumps({"summary": {"status": "warn"}}),
                "stderr": "",
                "ok": True,
            },
            {
                "command": ["plan", "--json"],
                "cwd": str(repo_root),
                "exit_code": 0,
                "stdout": json.dumps({"next_action": "phase2"}),
                "stderr": "",
                "ok": True,
            },
            {
                "command": ["stats"],
                "cwd": str(repo_root),
                "exit_code": 0,
                "stdout": "service status",
                "stderr": "",
                "ok": True,
            },
        ]
        result = runner.invoke(
            cli,
            ["--repo-root", str(repo_root), "--json", "status"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["doctor"]["summary"]["status"] == "warn"
        assert payload["plan"]["next_action"] == "phase2"
