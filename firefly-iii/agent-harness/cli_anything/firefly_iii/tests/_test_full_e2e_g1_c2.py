# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLIE2EMixin2:
    def test_cli_insights_overview(self):
        """Test CLI insights overview command"""
        result = self._run_cli([
            'insights', 'overview',
            '--start', '2024-01-01',
            '--end', '2024-01-31'
        ])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, (list, dict))
    def test_cli_search(self):
        """Test CLI search command"""
        result = self._run_cli(['search', 'transactions', '--query', 'test'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_info_status(self):
        """Test CLI info status command"""
        result = self._run_cli(['info', 'status'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        assert 'Firefly III connection is normal' in result.stdout
    def test_cli_help_shows_all_commands(self):
        """Test CLI help shows all command groups"""
        result = subprocess.run(
            ['python', '-m', 'cli_anything.firefly_iii', '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        output = result.stdout

        # Check all major command groups are documented
        expected_commands = [
            'accounts', 'transactions', 'budgets', 'categories', 'tags',
            'bills', 'piggy-banks', 'insights', 'search', 'export', 'info',
            'autocomplete', 'currencies', 'recurrences', 'rules',
            'rule-groups', 'summary', 'webhooks'
        ]

        for cmd in expected_commands:
            assert cmd in output, f"Command '{cmd}' not in help output"
