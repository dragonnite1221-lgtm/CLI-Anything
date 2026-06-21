# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestGeneratedCommandsImportMixin2:
    def test_invalid_data_json_reports_click_error(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.lists import lists_group

        result = CliRunner().invoke(lists_group, ["create", "--data", "{bad"])

        assert result.exit_code == 2
        assert "Invalid value for --data" in result.output
        assert "valid JSON" in result.output
        assert "Traceback" not in result.output
    def test_extra_params_must_be_json_object(self):
        from click.testing import CliRunner
        from cli_anything.mailchimp.commands.lists import lists_group

        result = CliRunner().invoke(lists_group, ["list", "--extra-params", "[]"])

        assert result.exit_code == 2
        assert "Invalid value for --extra-params" in result.output
        assert "JSON object" in result.output
        assert "Traceback" not in result.output
    def test_cli_without_subcommand_starts_repl_through_click(self):
        from click.testing import CliRunner
        import cli_anything.mailchimp.mailchimp_cli as mailchimp_cli

        with patch.object(mailchimp_cli, "_start_repl") as start_repl:
            result = CliRunner().invoke(mailchimp_cli.cli, [])

        assert result.exit_code == 0, result.output
        start_repl.assert_called_once_with()
