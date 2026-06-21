# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendErrorHandling:
    """Test error handling for server-down and bad-response scenarios."""

    def test_heartbeat_connection_error(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        import requests

        b._session.get.side_effect = requests.ConnectionError("Connection refused")
        with pytest.raises(requests.ConnectionError):
            b.heartbeat()

    def test_version_connection_error(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        import requests

        b._session.get.side_effect = requests.ConnectionError("Connection refused")
        with pytest.raises(requests.ConnectionError):
            b.version()

    def test_list_collections_http_error(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        import requests

        resp = MagicMock()
        resp.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        b._session.get.return_value = resp
        with pytest.raises(requests.HTTPError):
            b.list_collections()

    def test_get_collection_404(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        import requests

        resp = MagicMock()
        resp.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        b._session.get.return_value = resp
        with pytest.raises(requests.HTTPError):
            b.get_collection("nonexistent")
