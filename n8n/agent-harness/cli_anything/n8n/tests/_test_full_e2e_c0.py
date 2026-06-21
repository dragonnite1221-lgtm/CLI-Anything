# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _resolve_cli  # noqa: F401,E501


class _TestCLISubprocessMixin0:
    def test_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "n8n workflow automation" in result.stdout
    def test_version(self):
        result = subprocess.run(
            [*_resolve_cli(), "--version"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "2.4.7" in result.stdout
    def test_workflow_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "list" in result.stdout
        assert "set-tags" in result.stdout
        assert "transfer" in result.stdout
        assert "export" in result.stdout
        assert "import" in result.stdout
    def test_status_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "status", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "overview" in result.stdout.lower()
    def test_execution_watch_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "execution", "watch", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "interval" in result.stdout
    def test_config_test_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "config", "test", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "connection" in result.stdout.lower()
    def test_workflow_search_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "search", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "QUERY" in result.stdout
    def test_workflow_bulk_activate_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "bulk-activate", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--tag" in result.stdout
        assert "--search" in result.stdout
    def test_workflow_backup_all_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "backup-all", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--dir" in result.stdout
    def test_workflow_restore_all_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "restore-all", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--dry-run" in result.stdout
    def test_workflow_diff_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "diff", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "SOURCE" in result.stdout
    def test_execution_errors_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "execution", "errors", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--details" in result.stdout
    def test_template_search_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "template", "search", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "QUERY" in result.stdout
    def test_template_deploy_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "template", "deploy", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "TEMPLATE_ID" in result.stdout
    def test_workflow_validate_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "validate", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "SOURCE" in result.stdout
    def test_workflow_test_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "test", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "WORKFLOW_ID" in result.stdout
    def test_workflow_autofix_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "autofix", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--apply" in result.stdout
