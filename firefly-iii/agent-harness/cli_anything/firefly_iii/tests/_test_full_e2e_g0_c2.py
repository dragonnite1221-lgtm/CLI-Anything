# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EBackendMixin2:
    def test_search(self, backend):
        """Test search functionality"""
        result = backend.search('test')

        assert 'data' in result
        assert isinstance(result['data'], list)
    def test_chart_account_overview(self, backend):
        """Test account overview chart"""
        result = backend.get_chart_account_overview({
            "start": "2024-01-01",
            "end": "2024-01-31"
        })

        assert isinstance(result, (dict, list))
    def test_chart_balance(self, backend):
        """Test balance chart"""
        result = backend.get_chart_balance({
            "start": "2024-01-01",
            "end": "2024-01-31"
        })

        assert isinstance(result, (dict, list))
