# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestFireflyIIIBackendMethods:
    """Test all backend API methods exist and are callable"""

    @pytest.fixture
    def backend(self):
        """Create backend with mocked connection"""
        with patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {"version": "6.0.0"}}
            mock_get.return_value = mock_response
            return FireflyIIIBackend("https://firefly.example.com", "test-pat")

    def test_accounts_crud(self, backend):
        """Test account CRUD methods exist"""
        assert hasattr(backend, 'get_accounts')
        assert hasattr(backend, 'get_account')
        assert hasattr(backend, 'create_account')
        assert hasattr(backend, 'update_account')
        assert hasattr(backend, 'delete_account')

    def test_transactions_crud(self, backend):
        """Test transaction CRUD methods exist"""
        assert hasattr(backend, 'get_transactions')
        assert hasattr(backend, 'get_transaction')
        assert hasattr(backend, 'create_transaction')
        assert hasattr(backend, 'update_transaction')
        assert hasattr(backend, 'delete_transaction')

    def test_budgets_crud(self, backend):
        """Test budget CRUD methods exist"""
        assert hasattr(backend, 'get_budgets')
        assert hasattr(backend, 'get_budget')
        assert hasattr(backend, 'create_budget')
        assert hasattr(backend, 'update_budget')
        assert hasattr(backend, 'delete_budget')
        assert hasattr(backend, 'get_budget_limits')
        assert hasattr(backend, 'create_budget_limit')
        assert hasattr(backend, 'update_budget_limit')
        assert hasattr(backend, 'delete_budget_limit')

    def test_categories_crud(self, backend):
        """Test category CRUD methods exist"""
        assert hasattr(backend, 'get_categories')
        assert hasattr(backend, 'get_category')
        assert hasattr(backend, 'create_category')
        assert hasattr(backend, 'update_category')
        assert hasattr(backend, 'delete_category')

    def test_tags_crud(self, backend):
        """Test tag CRUD methods exist"""
        assert hasattr(backend, 'get_tags')
        assert hasattr(backend, 'get_tag')
        assert hasattr(backend, 'create_tag')
        assert hasattr(backend, 'update_tag')
        assert hasattr(backend, 'delete_tag')

    def test_bills_crud(self, backend):
        """Test bill CRUD methods exist"""
        assert hasattr(backend, 'get_bills')
        assert hasattr(backend, 'get_bill')
        assert hasattr(backend, 'create_bill')
        assert hasattr(backend, 'update_bill')
        assert hasattr(backend, 'delete_bill')

    def test_piggy_banks_crud(self, backend):
        """Test piggy bank CRUD methods exist"""
        assert hasattr(backend, 'get_piggy_banks')
        assert hasattr(backend, 'get_piggy_bank')
        assert hasattr(backend, 'create_piggy_bank')
        assert hasattr(backend, 'update_piggy_bank')
        assert hasattr(backend, 'delete_piggy_bank')
        assert hasattr(backend, 'get_piggy_bank_events')
        assert hasattr(backend, 'create_piggy_bank_event')

    def test_autocomplete_methods(self, backend):
        """Test autocomplete methods exist"""
        assert hasattr(backend, 'autocomplete_accounts')
        assert hasattr(backend, 'autocomplete_bills')
        assert hasattr(backend, 'autocomplete_budgets')
        assert hasattr(backend, 'autocomplete_categories')
        assert hasattr(backend, 'autocomplete_currencies')
        assert hasattr(backend, 'autocomplete_piggy_banks')
        assert hasattr(backend, 'autocomplete_tags')
        assert hasattr(backend, 'autocomplete_transactions')
        assert hasattr(backend, 'autocomplete_rule_groups')
        assert hasattr(backend, 'autocomplete_rules')
        assert hasattr(backend, 'autocomplete_recurring')
        assert hasattr(backend, 'autocomplete_object_groups')
        assert hasattr(backend, 'autocomplete_transaction_types')

    def test_currencies_crud(self, backend):
        """Test currency CRUD methods exist"""
        assert hasattr(backend, 'get_currencies')
        assert hasattr(backend, 'get_currency')
        assert hasattr(backend, 'create_currency')
        assert hasattr(backend, 'update_currency')
        assert hasattr(backend, 'delete_currency')
        assert hasattr(backend, 'get_currency_exchange_rates')

    def test_recurrences_crud(self, backend):
        """Test recurrence CRUD methods exist"""
        assert hasattr(backend, 'get_recurrences')
        assert hasattr(backend, 'get_recurrence')
        assert hasattr(backend, 'create_recurrence')
        assert hasattr(backend, 'update_recurrence')
        assert hasattr(backend, 'delete_recurrence')

    def test_rules_crud(self, backend):
        """Test rule CRUD methods exist"""
        assert hasattr(backend, 'get_rules')
        assert hasattr(backend, 'get_rule')
        assert hasattr(backend, 'create_rule')
        assert hasattr(backend, 'update_rule')
        assert hasattr(backend, 'delete_rule')
        assert hasattr(backend, 'test_rule')
        assert hasattr(backend, 'execute_rule')

    def test_rule_groups_crud(self, backend):
        """Test rule group CRUD methods exist"""
        assert hasattr(backend, 'get_rule_groups')
        assert hasattr(backend, 'get_rule_group')
        assert hasattr(backend, 'create_rule_group')
        assert hasattr(backend, 'update_rule_group')
        assert hasattr(backend, 'delete_rule_group')
        assert hasattr(backend, 'execute_rule_group')

    def test_summary_methods(self, backend):
        """Test summary methods exist"""
        assert hasattr(backend, 'get_summary')

    def test_webhooks_crud(self, backend):
        """Test webhook CRUD methods exist"""
        assert hasattr(backend, 'get_webhooks')
        assert hasattr(backend, 'get_webhook')
        assert hasattr(backend, 'create_webhook')
        assert hasattr(backend, 'update_webhook')
        assert hasattr(backend, 'delete_webhook')
        assert hasattr(backend, 'trigger_webhook')

    def test_chart_methods(self, backend):
        """Test chart methods exist"""
        assert hasattr(backend, 'get_chart_account_overview')
        assert hasattr(backend, 'get_chart_balance')
        assert hasattr(backend, 'get_chart_budget_overview')
        assert hasattr(backend, 'get_chart_category_overview')

    def test_other_methods(self, backend):
        """Test other utility methods exist"""
        assert hasattr(backend, 'get_insight')
        assert hasattr(backend, 'search')
        assert hasattr(backend, 'export_data')
        assert hasattr(backend, 'get_available_budgets')
        assert hasattr(backend, 'create_available_budget')
        assert hasattr(backend, 'get_object_groups')
        assert hasattr(backend, 'get_links')
        assert hasattr(backend, 'get_attachments')
        assert hasattr(backend, 'get_configuration')
        assert hasattr(backend, 'get_preferences')
        assert hasattr(backend, 'get_users')
        assert hasattr(backend, 'get_user_groups')
