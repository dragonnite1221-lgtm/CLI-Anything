# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendDocuments:
    """Test document operations with mocked HTTP."""

    def _make_backend(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        return b

    def _mock_response(self, json_data, text=""):
        resp = MagicMock()
        resp.json.return_value = json_data
        resp.text = text or json.dumps(json_data) if json_data else ""
        resp.raise_for_status.return_value = None
        return resp

    def test_add_documents_body(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(None, text="")
        b.add_documents("col-id", ids=["d1"], documents=["hello world"])
        body = b._session.post.call_args[1]["json"]
        assert body["ids"] == ["d1"]
        assert body["documents"] == ["hello world"]
        assert "metadatas" not in body

    def test_add_documents_with_metadatas(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(None, text="")
        b.add_documents(
            "col-id", ids=["d1"], documents=["text"], metadatas=[{"source": "test"}]
        )
        body = b._session.post.call_args[1]["json"]
        assert body["metadatas"] == [{"source": "test"}]

    def test_get_documents_url(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response({"ids": [], "documents": []})
        b.get_documents("col-id-123")
        called_url = b._session.post.call_args[0][0]
        assert "col-id-123/get" in called_url

    def test_get_documents_with_limit_offset(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response({"ids": [], "documents": []})
        b.get_documents("col-id", limit=10, offset=5)
        body = b._session.post.call_args[1]["json"]
        assert body["limit"] == 10
        assert body["offset"] == 5

    def test_delete_documents_body(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(None, text="")
        b.delete_documents("col-id", ids=["d1", "d2"])
        body = b._session.post.call_args[1]["json"]
        assert body["ids"] == ["d1", "d2"]

    def test_count_documents_url(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(42)
        result = b.count_documents("col-id")
        called_url = b._session.post.call_args[0][0]
        assert "col-id/count" in called_url
        assert result == 42


class TestBackendQuery:
    """Test semantic search query with mocked HTTP."""

    def _make_backend(self):
        b = ChromaDBBackend()
        b._session = MagicMock()
        return b

    def _mock_response(self, json_data):
        resp = MagicMock()
        resp.json.return_value = json_data
        resp.raise_for_status.return_value = None
        return resp

    def test_query_body(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response(
            {"ids": [[]], "documents": [[]]}
        )
        b.query("col-id", query_texts=["test query"], n_results=3)
        body = b._session.post.call_args[1]["json"]
        assert body["query_texts"] == ["test query"]
        assert body["n_results"] == 3

    def test_query_default_n_results(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response({"ids": [[]]})
        b.query("col-id", query_texts=["hello"])
        body = b._session.post.call_args[1]["json"]
        assert body["n_results"] == 5

    def test_query_url(self):
        b = self._make_backend()
        b._session.post.return_value = self._mock_response({"ids": [[]]})
        b.query("col-id-abc", query_texts=["x"])
        called_url = b._session.post.call_args[0][0]
        assert "col-id-abc/query" in called_url
