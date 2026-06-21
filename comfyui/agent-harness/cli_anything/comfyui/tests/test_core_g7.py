# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackend:
    """Test comfyui_backend HTTP wrappers."""

    def test_api_get_success(self):
        """api_get should return parsed JSON on success."""
        from cli_anything.comfyui.utils.comfyui_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"result": "ok"}'
        mock_resp.json.return_value = {"result": "ok"}
        mock_resp.raise_for_status = MagicMock()

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.get",
            return_value=mock_resp,
        ):
            result = api_get("http://localhost:8188", "/queue")

        assert result == {"result": "ok"}

    def test_api_get_connection_error(self):
        """api_get should raise RuntimeError on connection failure."""
        import requests as req
        from cli_anything.comfyui.utils.comfyui_backend import api_get

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.get",
            side_effect=req.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(RuntimeError, match="Cannot connect"):
                api_get("http://localhost:8188", "/queue")

    def test_api_post_success(self):
        """api_post should return parsed JSON on success."""
        from cli_anything.comfyui.utils.comfyui_backend import api_post

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"prompt_id": "abc"}'
        mock_resp.json.return_value = {"prompt_id": "abc"}
        mock_resp.raise_for_status = MagicMock()

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.post",
            return_value=mock_resp,
        ):
            result = api_post("http://localhost:8188", "/prompt", {"prompt": {}})

        assert result["prompt_id"] == "abc"

    def test_api_delete_success(self):
        """api_delete should return ok status on 204."""
        from cli_anything.comfyui.utils.comfyui_backend import api_delete

        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_resp.raise_for_status = MagicMock()

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.delete",
            return_value=mock_resp,
        ):
            result = api_delete("http://localhost:8188", "/queue")

        assert result == {"status": "ok"}

    def test_api_get_raw_returns_bytes(self):
        """api_get_raw should return raw bytes."""
        from cli_anything.comfyui.utils.comfyui_backend import api_get_raw

        fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = fake_bytes
        mock_resp.raise_for_status = MagicMock()

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.get",
            return_value=mock_resp,
        ):
            result = api_get_raw(
                "http://localhost:8188",
                "/view",
                params={"filename": "ComfyUI_00001_.png", "type": "output"},
            )

        assert result == fake_bytes

    def test_api_get_timeout_raises(self):
        """api_get should raise RuntimeError on timeout."""
        import requests as req
        from cli_anything.comfyui.utils.comfyui_backend import api_get

        with patch(
            "cli_anything.comfyui.utils.comfyui_backend.requests.get",
            side_effect=req.exceptions.Timeout(),
        ):
            with pytest.raises(RuntimeError, match="timed out"):
                api_get("http://localhost:8188", "/queue")
