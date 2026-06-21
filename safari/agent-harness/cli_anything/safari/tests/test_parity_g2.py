# ruff: noqa: F403, F405, E501
from .test_parity_helpers import *  # noqa: F403


class TestParityIntrospection:
    """The introspection commands (tools list/describe) reflect the registry."""

    def test_tools_count_command(self):
        runner = CliRunner()
        registry = load_registry()
        result = runner.invoke(cli, ["tools", "count"])
        assert result.exit_code == 0
        assert result.output.strip() == str(len(registry))

    def test_tools_list_outputs_every_tool(self):
        runner = CliRunner()
        registry = load_registry()
        result = runner.invoke(cli, ["tools", "list"])
        assert result.exit_code == 0
        for tool in registry:
            assert tool.short_name in result.output

    def test_tools_list_json_shape(self):
        import json

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "tools", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        registry = load_registry()
        assert len(data) == len(registry)
        for item in data:
            assert {"name", "short_name", "description", "param_count"} <= set(item)

    def test_tools_describe_known_tool(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["tools", "describe", "safari_scroll"])
        assert result.exit_code == 0
        assert "safari_scroll" in result.output
        assert "direction" in result.output
        assert "amount" in result.output

    def test_tools_describe_by_short_name(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["tools", "describe", "scroll"])
        assert result.exit_code == 0
        assert "safari_scroll" in result.output

    def test_tools_describe_unknown_rejects(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["tools", "describe", "does_not_exist"])
        assert result.exit_code != 0
