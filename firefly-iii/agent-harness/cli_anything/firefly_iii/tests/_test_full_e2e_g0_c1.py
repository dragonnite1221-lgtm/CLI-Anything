# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EBackendMixin1:
    def test_tags_crud_operations(self, backend):
        """Test tag CRUD operations"""
        import uuid
        test_tag = f"test-tag-{uuid.uuid4().hex[:8]}"

        # Create
        create_result = backend.create_tag({"tag": test_tag})
        assert 'data' in create_result
        tag_id = create_result['data']['id']

        # Read
        get_result = backend.get_tag(tag_id)
        assert get_result['data']['id'] == tag_id

        # Update
        update_result = backend.update_tag(tag_id, {"tag": test_tag + "-updated"})
        assert update_result['data']['attributes']['tag'] == test_tag + "-updated"

        # Delete
        delete_result = backend.delete_tag(tag_id)
        assert delete_result.get('status') == 'success'
    def test_bills_list(self, backend):
        """Test getting bill list"""
        result = backend.get_bills()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_piggy_banks_list(self, backend):
        """Test getting piggy bank list"""
        result = backend.get_piggy_banks()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_autocomplete_accounts(self, backend):
        """Test autocomplete accounts"""
        result = backend.autocomplete_accounts({"limit": 5})

        assert isinstance(result, list)
    def test_autocomplete_categories(self, backend):
        """Test autocomplete categories"""
        result = backend.autocomplete_categories({"limit": 5})

        assert isinstance(result, list)
    def test_autocomplete_tags(self, backend):
        """Test autocomplete tags"""
        result = backend.autocomplete_tags({"limit": 5})

        assert isinstance(result, list)
    def test_currencies_list(self, backend):
        """Test getting currency list"""
        result = backend.get_currencies()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_recurrences_list(self, backend):
        """Test getting recurring transaction list"""
        result = backend.get_recurrences()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_rules_list(self, backend):
        """Test getting rule list"""
        result = backend.get_rules()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_rule_groups_list(self, backend):
        """Test getting rule group list"""
        result = backend.get_rule_groups()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_summary_default_set(self, backend):
        """Test summary default set - may not exist in all Firefly III versions"""
        try:
            result = backend.get_summary("default-set", {
                "start": "2024-01-01",
                "end": "2024-01-31"
            })
            assert isinstance(result, (dict, list))
        except RuntimeError as e:
            if "Resource not found" in str(e):
                pytest.skip("summary/default-set endpoint not available")
            raise
    def test_webhooks_list(self, backend):
        """Test getting webhook list"""
        result = backend.get_webhooks()

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_insights_expense(self, backend):
        """Test expense insight reports"""
        result = backend.get_insight('expense/category', {
            'start': '2024-01-01',
            'end': '2024-01-31'
        })

        assert isinstance(result, (list, dict))
        if isinstance(result, dict):
            assert 'data' in result
    def test_insights_income(self, backend):
        """Test income insight reports"""
        result = backend.get_insight('income/category', {
            'start': '2024-01-01',
            'end': '2024-01-31'
        })

        assert isinstance(result, (list, dict))
        if isinstance(result, dict):
            assert 'data' in result
