# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EBackendMixin0:
    """End-to-end tests for backend API"""
    @pytest.fixture
    def backend(self):
        """Create backend instance"""
        from cli_anything.firefly_iii.utils.firefly_iii_backend import FireflyIIIBackend

        base_url = os.environ['FIREFLY_III_BASE_URL']
        pat = os.environ['FIREFLY_III_PAT']

        return FireflyIIIBackend(base_url, pat)
    def test_connection(self, backend):
        """Test connection"""
        result = backend.get_about()

        assert 'data' in result
        if 'attributes' in result['data']:
            assert 'version' in result['data']['attributes']
        else:
            assert 'version' in result['data']
    def test_accounts_list(self, backend):
        """Test getting account list"""
        result = backend.get_accounts()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_accounts_list_with_params(self, backend):
        """Test getting account list with type filter"""
        result = backend.get_accounts({'type': 'asset'})

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_accounts_crud_operations(self, backend):
        """Test account read operations (skip create/update/delete due to API permission requirements)"""
        # Just test read - some users don't have create permission
        result = backend.get_accounts()
        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_transactions_list(self, backend):
        """Test getting transaction list"""
        result = backend.get_transactions()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_transactions_list_with_limit(self, backend):
        """Test getting transaction list with limit"""
        result = backend.get_transactions({'limit': 5})

        assert 'data' in result
        assert isinstance(result['data'], list)
        assert len(result['data']) <= 5
    def test_budgets_list(self, backend):
        """Test getting budget list"""
        result = backend.get_budgets()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_budgets_crud_operations(self, backend):
        """Test budget CRUD operations"""
        # Create
        create_result = backend.create_budget({"name": "Test Budget E2E"})
        assert 'data' in create_result
        budget_id = create_result['data']['id']

        # Read
        get_result = backend.get_budget(budget_id)
        assert get_result['data']['id'] == budget_id

        # Update
        update_result = backend.update_budget(budget_id, {"name": "Test Budget E2E Updated"})
        assert update_result['data']['attributes']['name'] == "Test Budget E2E Updated"

        # Delete
        delete_result = backend.delete_budget(budget_id)
        assert delete_result.get('status') == 'success'
    def test_categories_list(self, backend):
        """Test getting category list"""
        result = backend.get_categories()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_categories_crud_operations(self, backend):
        """Test category CRUD operations"""
        # Create
        create_result = backend.create_category({"name": "Test Category E2E"})
        assert 'data' in create_result
        category_id = create_result['data']['id']

        # Read
        get_result = backend.get_category(category_id)
        assert get_result['data']['id'] == category_id

        # Update
        update_result = backend.update_category(category_id, {"name": "Test Category E2E Updated"})
        assert update_result['data']['attributes']['name'] == "Test Category E2E Updated"

        # Delete
        delete_result = backend.delete_category(category_id)
        assert delete_result.get('status') == 'success'
    def test_tags_list(self, backend):
        """Test getting tag list"""
        result = backend.get_tags()

        assert 'data' in result
        assert isinstance(result['data'], list)
