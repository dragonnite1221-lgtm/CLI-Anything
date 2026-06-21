# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestConfig:
    def test_load_config_missing_file(self, tmp_path):
        with patch(
            "cli_anything.anygen.utils.anygen_backend.CONFIG_FILE",
            tmp_path / "nope.json",
        ):
            assert load_config() == {}

    def test_save_and_load_config(self, tmp_path):
        cfg_file = tmp_path / "cfg" / "config.json"
        with (
            patch(
                "cli_anything.anygen.utils.anygen_backend.CONFIG_DIR", tmp_path / "cfg"
            ),
            patch("cli_anything.anygen.utils.anygen_backend.CONFIG_FILE", cfg_file),
        ):
            save_config({"api_key": "sk-test123"})
            assert cfg_file.exists()
            result = load_config()
            assert result["api_key"] == "sk-test123"

    def test_api_key_priority_cli_arg(self):
        assert get_api_key("sk-cli") == "sk-cli"

    def test_api_key_priority_env(self, monkeypatch):
        monkeypatch.setenv("ANYGEN_API_KEY", "sk-env")
        assert get_api_key(None) == "sk-env"

    def test_make_auth_token_bare(self):
        assert _make_auth_token("sk-test") == "Bearer sk-test"

    def test_make_auth_token_already_bearer(self):
        assert _make_auth_token("Bearer sk-test") == "Bearer sk-test"

    def test_require_api_key_raises(self):
        with pytest.raises(RuntimeError, match="API key not found"):
            _require_api_key(None)

    def test_require_api_key_returns(self):
        assert _require_api_key("sk-ok") == "sk-ok"


class TestCreateTask:
    def _mock_response(self, status_code=200, json_data=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or {}
        resp.text = json.dumps(json_data or {})
        return resp

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_slide_task(self, mock_post):
        mock_post.return_value = self._mock_response(
            200,
            {
                "success": True,
                "task_id": "task_001",
                "task_url": "https://anygen.io/task/001",
            },
        )
        from cli_anything.anygen.utils.anygen_backend import create_task

        result = create_task(
            "sk-test", "slide", "Make a presentation", language="en-US", slide_count=10
        )
        assert result["task_id"] == "task_001"
        body = mock_post.call_args[1]["json"]
        assert body["operation"] == "slide"
        assert body["slide_count"] == 10

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_doc_minimal(self, mock_post):
        mock_post.return_value = self._mock_response(
            200, {"success": True, "task_id": "task_002"}
        )
        from cli_anything.anygen.utils.anygen_backend import create_task

        result = create_task("sk-test", "doc", "Write a report")
        assert result["task_id"] == "task_002"

    def test_create_invalid_operation(self):
        from cli_anything.anygen.utils.anygen_backend import create_task

        with pytest.raises(ValueError, match="Invalid operation"):
            create_task("sk-test", "invalid_op", "test")

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_with_file_tokens(self, mock_post):
        mock_post.return_value = self._mock_response(
            200, {"success": True, "task_id": "task_003"}
        )
        from cli_anything.anygen.utils.anygen_backend import create_task

        create_task("sk-test", "slide", "test", file_tokens=["tk_a", "tk_b"])
        body = mock_post.call_args[1]["json"]
        assert body["file_tokens"] == ["tk_a", "tk_b"]

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_with_style(self, mock_post):
        mock_post.return_value = self._mock_response(
            200, {"success": True, "task_id": "task_004"}
        )
        from cli_anything.anygen.utils.anygen_backend import create_task

        create_task("sk-test", "slide", "test prompt", style="business formal")
        body = mock_post.call_args[1]["json"]
        assert "Style requirement: business formal" in body["prompt"]

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_http_error(self, mock_post):
        mock_post.return_value = self._mock_response(500, {})
        from cli_anything.anygen.utils.anygen_backend import create_task

        with pytest.raises(RuntimeError, match="HTTP 500"):
            create_task("sk-test", "slide", "test")

    @patch("cli_anything.anygen.utils.anygen_backend.requests.post")
    def test_create_api_error(self, mock_post):
        mock_post.return_value = self._mock_response(
            200, {"success": False, "error": "quota exceeded"}
        )
        from cli_anything.anygen.utils.anygen_backend import create_task

        with pytest.raises(RuntimeError, match="quota exceeded"):
            create_task("sk-test", "slide", "test")
