# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestOutput:
    """Test output formatting"""

    def test_json_output(self, capsys):
        """Test JSON output"""
        from cli_anything.firefly_iii.firefly_iii_cli import output
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        cli_module._json_output = True
        test_data = {"key": "value"}

        output(test_data)

        captured = capsys.readouterr()
        assert json.loads(captured.out) == test_data

    def test_human_readable_output(self, capsys):
        """Test human-readable output"""
        from cli_anything.firefly_iii.firefly_iii_cli import output
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        cli_module._json_output = False
        test_data = {"data": [{"id": 1, "attributes": {"name": "Test Account"}}]}

        output(test_data)

        captured = capsys.readouterr()
        assert "Test Account" in captured.out

    def test_human_readable_list_output(self, capsys):
        """Test human-readable list output"""
        from cli_anything.firefly_iii.firefly_iii_cli import output
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        cli_module._json_output = False
        test_data = [{"name": "Item 1"}, {"name": "Item 2"}]

        output(test_data)

        captured = capsys.readouterr()
        assert "Item 1" in captured.out
        assert "Item 2" in captured.out

    def test_human_readable_plain_dict(self, capsys):
        """Test human-readable output with plain dict"""
        from cli_anything.firefly_iii.firefly_iii_cli import output
        import cli_anything.firefly_iii.firefly_iii_cli as cli_module

        cli_module._json_output = False
        test_data = {"key": "value", "count": 42}

        output(test_data)

        captured = capsys.readouterr()
        assert "key" in captured.out
        assert "value" in captured.out


class TestCommandGroups:
    """Test CLI command groups are registered"""

    def test_all_command_groups_importable(self):
        """Test all command groups can be imported"""
        from cli_anything.firefly_iii.core import (
            accounts, transactions, budgets, categories, tags,
            bills, piggy_banks, insights, search, export, info,
            autocomplete, currencies, recurrences, rules,
            rule_groups, summary, webhooks
        )

        assert accounts is not None
        assert transactions is not None
        assert budgets is not None
        assert categories is not None
        assert tags is not None
        assert bills is not None
        assert piggy_banks is not None
        assert insights is not None
        assert search is not None
        assert export is not None
        assert info is not None
        assert autocomplete is not None
        assert currencies is not None
        assert recurrences is not None
        assert rules is not None
        assert rule_groups is not None
        assert summary is not None
        assert webhooks is not None

    def test_cli_has_all_commands(self):
        """Test CLI has all expected commands registered"""
        from cli_anything.firefly_iii.firefly_iii_cli import cli

        expected_commands = [
            'accounts', 'transactions', 'budgets', 'categories', 'tags',
            'bills', 'piggy-banks', 'insights', 'search', 'export', 'info',
            'autocomplete', 'currencies', 'recurrences', 'rules',
            'rule-groups', 'summary', 'webhooks'
        ]

        for cmd in expected_commands:
            assert cmd in cli.commands, f"Command '{cmd}' not registered"
