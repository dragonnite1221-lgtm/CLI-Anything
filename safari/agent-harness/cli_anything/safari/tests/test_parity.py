# ruff: noqa: F403, F405, E501
from .test_parity_helpers import *  # noqa: F403


class TestParityToolCoverage:
    """Every tool in the registry must be reachable as a Click subcommand."""

    def setup_method(self):
        self.registry = load_registry()

    def test_registry_not_empty(self):
        assert len(self.registry) > 0, "tools.json is empty"

    def test_registry_tool_count_matches_expected(self):
        # safari-mcp v2.7.8 exposes 84 tools. Update this when bumping upstream.
        assert len(self.registry) == 84, (
            f"Expected 84 tools from safari-mcp, got {len(self.registry)}. "
            f"Re-run scripts/extract_tools.py if safari-mcp was upgraded."
        )

    def test_every_tool_reachable_via_tool_group(self):
        """For each tool in the registry, `safari tool <short-name>` exists."""
        runner = CliRunner()
        missing = []
        for tool in self.registry:
            result = runner.invoke(
                cli,
                ["tool", tool.short_name, "--help"],
                catch_exceptions=False,
            )
            if result.exit_code != 0:
                missing.append(tool.short_name)
        assert not missing, f"Tools missing from CLI: {missing}"

    def test_tool_group_has_exactly_registry_count(self):
        """The number of Click subcommands must equal the registry size."""
        ctx_commands = tool_group.commands
        assert len(ctx_commands) == len(self.registry), (
            f"tool group has {len(ctx_commands)} commands, "
            f"registry has {len(self.registry)} tools"
        )

    def test_no_unexpected_tools_in_cli(self):
        """Every Click subcommand under `tool` must come from the registry."""
        registry_short_names = {t.short_name for t in self.registry}
        cli_names = set(tool_group.commands.keys())
        extras = cli_names - registry_short_names
        assert not extras, f"Unexpected tools in CLI (not in registry): {extras}"
