# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403
from ._test_full_e2e_p0 import _resolve_cli  # noqa: F401,E501


class _TestCLISubprocessMixin1:
    def test_workflow_patch_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "patch", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--rename" in result.stdout
        assert "--enable-node" in result.stdout
        assert "--remove-node" in result.stdout
        assert "--connect" in result.stdout
    def test_health_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "health", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--diagnostic" in result.stdout
    def test_workflow_versions_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "versions", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "rollback" in result.stdout
        assert "prune" in result.stdout
        assert "stats" in result.stdout
    def test_workflow_scaffold_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "scaffold", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "webhook" in result.stdout
        assert "ai-agent" in result.stdout
    def test_workflow_patterns(self):
        result = subprocess.run(
            [*_resolve_cli(), "workflow", "patterns"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "webhook" in result.stdout
        assert "database" in result.stdout
    def test_expression_validate_valid(self):
        result = subprocess.run(
            [*_resolve_cli(), "expression", "={{$json.name}}"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "valid" in result.stdout.lower()
    def test_expression_validate_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "expression", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
    def test_node_search_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "node", "search", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "QUERY" in result.stdout
    def test_node_info_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "node", "info", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "PACKAGE_NAME" in result.stdout
    def test_completions_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "completions", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "bash" in result.stdout
    def test_credential_help(self):
        result = subprocess.run(
            [*_resolve_cli(), "credential", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "create" in result.stdout
        assert "schema" in result.stdout
        assert "transfer" in result.stdout
        # "list" command should not appear as a subcommand
        lines = [line.strip() for line in result.stdout.splitlines()]
        subcommands = [line for line in lines if line and not line.startswith("Usage") and not line.startswith("-") and not line.startswith("Options") and not line.startswith("Credential")]
        assert not any(line.startswith("list") for line in subcommands)
    def test_config_show_json(self):
        result = subprocess.run(
            [*_resolve_cli(), "--json", "config", "show"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
    def test_no_table_command(self):
        result = subprocess.run(
            [*_resolve_cli(), "table", "--help"], capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0  # table command removed
