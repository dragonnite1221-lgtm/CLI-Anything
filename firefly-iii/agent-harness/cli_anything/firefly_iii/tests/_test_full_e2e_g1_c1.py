# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLIE2EMixin1:
    def test_cli_piggy_banks_list(self):
        """Test CLI piggy banks list command"""
        result = self._run_cli(['piggy-banks', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_autocomplete_accounts(self):
        """Test CLI autocomplete accounts command"""
        result = self._run_cli(['autocomplete', 'accounts', '--limit', '3'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, list)
    def test_cli_autocomplete_categories(self):
        """Test CLI autocomplete categories command"""
        result = self._run_cli(['autocomplete', 'categories', '--limit', '3'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, list)
    def test_cli_autocomplete_tags(self):
        """Test CLI autocomplete tags command"""
        result = self._run_cli(['autocomplete', 'tags', '--limit', '3'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, list)
    def test_cli_currencies_list(self):
        """Test CLI currencies list command"""
        result = self._run_cli(['currencies', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_recurrences_list(self):
        """Test CLI recurrences list command"""
        result = self._run_cli(['recurrences', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_rules_list(self):
        """Test CLI rules list command"""
        result = self._run_cli(['rules', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_rule_groups_list(self):
        """Test CLI rule-groups list command"""
        result = self._run_cli(['rule-groups', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_summary_default_set(self):
        """Test CLI summary default-set command - may not exist in all Firefly III versions"""
        result = self._run_cli(['summary', 'default-set', '--start', '2024-01-01', '--end', '2024-01-31'])

        if result.returncode != 0:
            if "Resource not found" in result.stderr:
                pytest.skip("summary/default-set endpoint not available")
            pytest.fail(f"Unexpected error: {result.stderr}")

        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))
    def test_cli_webhooks_list(self):
        """Test CLI webhooks list command"""
        result = self._run_cli(['webhooks', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_insights_expense(self):
        """Test CLI insights expense command"""
        result = self._run_cli([
            'insights', 'expense',
            '--start', '2024-01-01',
            '--end', '2024-01-31'
        ])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, (list, dict))
    def test_cli_insights_income(self):
        """Test CLI insights income command"""
        result = self._run_cli([
            'insights', 'income',
            '--start', '2024-01-01',
            '--end', '2024-01-31'
        ])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, (list, dict))
    def test_cli_insights_transfer(self):
        """Test CLI insights transfer command"""
        result = self._run_cli([
            'insights', 'transfer',
            '--start', '2024-01-01',
            '--end', '2024-01-31'
        ])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, (list, dict))
