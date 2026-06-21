# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestCLIClick:
    """Test CLI structure with Click"""

    def test_cli_is_click_group(self):
        """Test CLI is a Click group"""
        from click import Group
        from cli_anything.firefly_iii.firefly_iii_cli import cli

        assert isinstance(cli, Group)

    def test_subcommands_are_click_groups(self):
        """Test subcommands are Click groups"""
        from click import Group
        from cli_anything.firefly_iii.firefly_iii_cli import cli

        # Get commands from the CLI group
        accounts = cli.commands.get('accounts')
        transactions = cli.commands.get('transactions')
        budgets = cli.commands.get('budgets')

        assert accounts is not None
        assert transactions is not None
        assert budgets is not None
        assert isinstance(accounts, Group)
        assert isinstance(transactions, Group)
        assert isinstance(budgets, Group)

    def test_accounts_subcommands(self):
        """Test accounts has expected subcommands"""
        from cli_anything.firefly_iii.core.accounts import accounts

        expected = ['list', 'get', 'create', 'update', 'delete']
        for cmd in expected:
            assert cmd in accounts.commands, f"accounts.{cmd} not found"

    def test_transactions_subcommands(self):
        """Test transactions has expected subcommands"""
        from cli_anything.firefly_iii.core.transactions import transactions

        expected = ['list', 'get', 'create', 'update', 'delete']
        for cmd in expected:
            assert cmd in transactions.commands, f"transactions.{cmd} not found"

    def test_budgets_subcommands(self):
        """Test budgets has expected subcommands"""
        from cli_anything.firefly_iii.core.budgets import budgets

        expected = ['list', 'get', 'create', 'update', 'delete', 'limits', 'limit-create', 'limit-update', 'limit-delete']
        for cmd in expected:
            assert cmd in budgets.commands, f"budgets.{cmd} not found"

    def test_autocomplete_subcommands(self):
        """Test autocomplete has expected subcommands"""
        from cli_anything.firefly_iii.core.autocomplete import autocomplete

        expected = [
            'accounts', 'bills', 'budgets', 'categories', 'currencies',
            'piggy-banks', 'tags', 'transactions', 'rule-groups', 'rules',
            'recurring', 'object-groups', 'transaction-types'
        ]
        for cmd in expected:
            assert cmd in autocomplete.commands, f"autocomplete.{cmd} not found"

    def test_rules_subcommands(self):
        """Test rules has expected subcommands"""
        from cli_anything.firefly_iii.core.rules import rules

        expected = ['list', 'get', 'create', 'update', 'delete', 'test', 'execute']
        for cmd in expected:
            assert cmd in rules.commands, f"rules.{cmd} not found"

    def test_webhooks_subcommands(self):
        """Test webhooks has expected subcommands"""
        from cli_anything.firefly_iii.core.webhooks import webhooks

        expected = ['list', 'get', 'create', 'update', 'delete', 'trigger']
        for cmd in expected:
            assert cmd in webhooks.commands, f"webhooks.{cmd} not found"

    def test_repl_dispatches_click_command_with_quoted_args(self):
        """Test REPL dispatches parsed input through Click and preserves quotes"""
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        class FakeReplSkin:
            prompts = ['probe "two words"', 'exit']

            def __init__(self, *args, **kwargs):
                pass

            def print_banner(self):
                pass

            def info(self, message):
                pass

            def prompt(self, prompt_name):
                return self.prompts.pop(0)

            def print_goodbye(self):
                pass

            def error(self, message):
                raise AssertionError(f"Unexpected REPL error: {message}")

            def help(self, commands):
                pass

        @click.command(name="probe")
        @click.argument("value")
        def probe(value):
            click.echo(f"value={value}")

        original_probe = cli_module.cli.commands.get("probe")
        cli_module.cli.add_command(probe)

        try:
            runner = CliRunner()
            with patch.object(cli_module, "FireflyIIIBackend", return_value=Mock()), \
                 patch.object(cli_module, "ReplSkin", FakeReplSkin):
                result = runner.invoke(
                    cli_module.cli,
                    ["--base-url", "https://firefly.example.com", "--pat", "test-pat"],
                )
        finally:
            if original_probe is None:
                cli_module.cli.commands.pop("probe", None)
            else:
                cli_module.cli.commands["probe"] = original_probe

        assert result.exit_code == 0
        assert "value=two words" in result.output

    def test_repl_click_error_remains_interactive(self):
        """Test Click parser errors are reported without exiting the REPL"""
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        class FakeReplSkin:
            prompts = ["probe-error --unknown", "exit"]
            instances = []

            def __init__(self, *args, **kwargs):
                self.errors = []
                self.goodbye_printed = False
                self.instances.append(self)

            def print_banner(self):
                pass

            def info(self, message):
                pass

            def prompt(self, prompt_name):
                return self.prompts.pop(0)

            def print_goodbye(self):
                self.goodbye_printed = True

            def error(self, message):
                self.errors.append(message)

            def help(self, commands):
                pass

        @click.command(name="probe-error")
        @click.option("--known")
        def probe_error(known):
            click.echo(f"known={known}")

        original_probe = cli_module.cli.commands.get("probe-error")
        cli_module.cli.add_command(probe_error)

        try:
            runner = CliRunner()
            with patch.object(cli_module, "FireflyIIIBackend", return_value=Mock()), \
                 patch.object(cli_module, "ReplSkin", FakeReplSkin):
                result = runner.invoke(
                    cli_module.cli,
                    ["--base-url", "https://firefly.example.com", "--pat", "test-pat"],
                )
        finally:
            if original_probe is None:
                cli_module.cli.commands.pop("probe-error", None)
            else:
                cli_module.cli.commands["probe-error"] = original_probe

        assert result.exit_code == 0
        skin = FakeReplSkin.instances[-1]
        assert any("No such option" in error for error in skin.errors)
        assert skin.goodbye_printed is True
