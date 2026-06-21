# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendURLConstruction:
    """Verify that the backend builds correct API URLs."""

    def test_default_base_url(self):
        b = ChromaDBBackend()
        assert b.base_url == "http://localhost:8000"

    def test_custom_base_url(self):
        b = ChromaDBBackend(base_url="http://myhost:9090")
        assert b.base_url == "http://myhost:9090"

    def test_trailing_slash_stripped(self):
        b = ChromaDBBackend(base_url="http://localhost:8000/")
        assert b.base_url == "http://localhost:8000"

    def test_tenant_db_prefix(self):
        b = ChromaDBBackend()
        expected = "http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database"
        assert b._tenant_db_prefix == expected

    def test_custom_tenant_and_database(self):
        b = ChromaDBBackend(tenant="my_tenant", database="my_db")
        expected = "http://localhost:8000/api/v2/tenants/my_tenant/databases/my_db"
        assert b._tenant_db_prefix == expected

    def test_session_headers(self):
        b = ChromaDBBackend()
        assert b._session.headers["Content-Type"] == "application/json"


class TestBackendServerCommands:
    """Test server heartbeat and version with mocked HTTP."""

    @patch("cli_anything.chromadb.utils.chromadb_backend.requests.Session")
    def test_heartbeat_url(self, MockSession):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"nanosecond_heartbeat": 1234567890}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        MockSession.return_value = mock_session

        b = ChromaDBBackend()
        result = b.heartbeat()

        mock_session.get.assert_called_with("http://localhost:8000/api/v2/heartbeat")
        assert result == {"nanosecond_heartbeat": 1234567890}

    @patch("cli_anything.chromadb.utils.chromadb_backend.requests.Session")
    def test_version_url(self, MockSession):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = "0.6.0"
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        MockSession.return_value = mock_session

        b = ChromaDBBackend()
        result = b.version()

        mock_session.get.assert_called_with("http://localhost:8000/api/v2/version")
        assert result == "0.6.0"


class TestBackendCollections:
    """Test collection CRUD with mocked HTTP."""

    def _make_backend(self):
        """Create a backend with a mocked session."""
        b = ChromaDBBackend()
        b._session = MagicMock()
        return b

    def _mock_response(self, json_data, status_code=200):
        resp = MagicMock()
        resp.json.return_value = json_data
        resp.status_code = status_code
        resp.raise_for_status.return_value = None
        return resp

    def test_list_collections_url(self):
        b = self._make_backend()
        b._session.get.return_value = self._mock_response([])
        b.list_collections()
        called_url = b._session.get.call_args[0][0]
        assert "/collections" in called_url
        assert "/tenants/default_tenant/databases/default_database" in called_url

    def test_list_collections_returns_list(self):
        b = self._make_backend()
        collections = [{"name": "test", "id": "abc-123"}]
        b._session.get.return_value = self._mock_response(collections)
        result = b.list_collections()
        assert isinstance(result, list)
        assert result[0]["name"] == "test"

    def test_create_collection_sends_name(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(
            {"name": "new_col", "id": "xyz"}
        )
        result = b.create_collection("new_col")
        call_kwargs = b._session.post.call_args
        assert call_kwargs[1]["json"]["name"] == "new_col"
        assert result["name"] == "new_col"

    def test_create_collection_with_metadata(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response({"name": "c", "id": "x"})
        b.create_collection("c", metadata={"key": "val"})
        body = b._session.post.call_args[1]["json"]
        assert body["metadata"] == {"key": "val"}

    def test_get_collection_url(self):
        b = self._make_backend()
        b._session.get.return_value = self._mock_response(
            {"name": "hub_knowledge", "id": "abc"}
        )
        b.get_collection("hub_knowledge")
        called_url = b._session.get.call_args[0][0]
        assert called_url.endswith("/collections/hub_knowledge")

    def test_delete_collection_returns_true(self):
        b = self._make_backend()
        b._session.delete.return_value = self._mock_response(None)
        result = b.delete_collection("old_col")
        assert result is True
