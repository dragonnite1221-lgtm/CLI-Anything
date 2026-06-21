# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestFireflyIIIBackend:
    """Test Firefly III backend client"""

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    def test_init_success(self, mock_get):
        """Test successful initialization"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"version": "6.0.0"}}
        mock_get.return_value = mock_response

        backend = FireflyIIIBackend("https://firefly.example.com", "test-pat")

        assert backend.base_url == "https://firefly.example.com"
        assert backend.pat == "test-pat"
        assert backend.headers['Authorization'] == 'Bearer test-pat'

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    def test_init_connection_error(self, mock_get):
        """Test connection error"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()

        with pytest.raises(RuntimeError) as exc_info:
            FireflyIIIBackend("https://firefly.example.com", "test-pat")

        assert "Cannot connect to Firefly III instance" in str(exc_info.value)

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    def test_init_auth_error(self, mock_get):
        """Test authentication error"""
        from requests.exceptions import HTTPError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            FireflyIIIBackend("https://firefly.example.com", "invalid-pat")

        assert "Authentication failed" in str(exc_info.value)

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.request')
    def test_get_request(self, mock_request, mock_get):
        """Test GET request"""
        # Mock validation request during initialization
        mock_init_response = Mock()
        mock_init_response.status_code = 200
        mock_init_response.json.return_value = {"data": {"version": "6.0.0"}}
        mock_get.return_value = mock_init_response

        # Mock actual request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": 1, "name": "Test"}]}
        mock_request.return_value = mock_response

        backend = FireflyIIIBackend("https://firefly.example.com", "test-pat")
        result = backend.get("/accounts")

        assert result["data"][0]["name"] == "Test"
        mock_request.assert_called_once()

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.request')
    def test_post_request(self, mock_request, mock_get):
        """Test POST request"""
        # Mock validation request during initialization
        mock_init_response = Mock()
        mock_init_response.status_code = 200
        mock_init_response.json.return_value = {"data": {"version": "6.0.0"}}
        mock_get.return_value = mock_init_response

        # Mock actual request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": 1}}
        mock_request.return_value = mock_response

        backend = FireflyIIIBackend("https://firefly.example.com", "test-pat")
        result = backend.post("/accounts", data={"name": "Test"})

        assert result["data"]["id"] == 1

    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.get')
    @patch('cli_anything.firefly_iii.utils.firefly_iii_backend.requests.request')
    def test_delete_request_returns_204(self, mock_request, mock_get):
        """Test DELETE request with 204 response"""
        mock_init_response = Mock()
        mock_init_response.status_code = 200
        mock_init_response.json.return_value = {"data": {"version": "6.0.0"}}
        mock_get.return_value = mock_init_response

        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        backend = FireflyIIIBackend("https://firefly.example.com", "test-pat")
        result = backend.delete("/accounts/1")

        assert result["status"] == "success"
        assert result["code"] == 204
