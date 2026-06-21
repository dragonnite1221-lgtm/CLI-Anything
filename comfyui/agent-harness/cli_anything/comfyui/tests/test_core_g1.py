# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestQueuePrompt:
    """Test submitting prompts to the queue."""

    def test_queue_prompt_success(self, sample_workflow):
        """Should return prompt_id and queue position."""
        mock_response = {
            "prompt_id": "abc-123-def",
            "number": 0,
            "node_errors": {},
        }
        with patch(
            "cli_anything.comfyui.core.queue.api_post", return_value=mock_response
        ):
            result = queue_mod.queue_prompt("http://localhost:8188", sample_workflow)

        assert result["prompt_id"] == "abc-123-def"
        assert result["number"] == 0
        assert result["node_errors"] == {}
        assert "client_id" in result

    def test_queue_prompt_with_client_id(self, sample_workflow):
        """Should use provided client_id."""
        mock_response = {"prompt_id": "xyz", "number": 1, "node_errors": {}}
        with patch(
            "cli_anything.comfyui.core.queue.api_post", return_value=mock_response
        ) as mock_post:
            result = queue_mod.queue_prompt(
                "http://localhost:8188", sample_workflow, client_id="my-client"
            )

        assert result["client_id"] == "my-client"
        call_args = mock_post.call_args
        assert call_args[0][2]["client_id"] == "my-client"

    def test_queue_empty_workflow_raises(self):
        """Should raise RuntimeError for empty workflow."""
        with pytest.raises(RuntimeError, match="empty"):
            queue_mod.queue_prompt("http://localhost:8188", {})

    def test_queue_prompt_server_error_raises(self, sample_workflow):
        """Should raise RuntimeError when server returns error."""
        mock_response = {"error": {"message": "Invalid prompt", "type": "value_error"}}
        with patch(
            "cli_anything.comfyui.core.queue.api_post", return_value=mock_response
        ):
            with pytest.raises(RuntimeError, match="rejected"):
                queue_mod.queue_prompt("http://localhost:8188", sample_workflow)


class TestQueueStatus:
    """Test queue status retrieval."""

    def test_get_queue_status(self):
        """Should return running and pending counts."""
        mock_response = {
            "queue_running": [["abc", {}, {}, {}]],
            "queue_pending": [["def", {}, {}, {}], ["ghi", {}, {}, {}]],
        }
        with patch(
            "cli_anything.comfyui.core.queue.api_get", return_value=mock_response
        ):
            result = queue_mod.get_queue_status("http://localhost:8188")

        assert result["running_count"] == 1
        assert result["pending_count"] == 2

    def test_get_queue_status_empty(self):
        """Should handle empty queue."""
        mock_response = {"queue_running": [], "queue_pending": []}
        with patch(
            "cli_anything.comfyui.core.queue.api_get", return_value=mock_response
        ):
            result = queue_mod.get_queue_status("http://localhost:8188")

        assert result["running_count"] == 0
        assert result["pending_count"] == 0


class TestQueueClear:
    """Test queue clearing."""

    def test_clear_queue(self):
        """Should return cleared status."""
        with patch(
            "cli_anything.comfyui.core.queue.api_delete", return_value={"status": "ok"}
        ):
            result = queue_mod.clear_queue("http://localhost:8188")

        assert result["status"] == "cleared"

    def test_clear_queue_passes_clear_flag(self):
        """Should pass clear=True to the API."""
        with patch(
            "cli_anything.comfyui.core.queue.api_delete", return_value={}
        ) as mock_del:
            queue_mod.clear_queue("http://localhost:8188")

        call_args = mock_del.call_args
        # data kwarg or positional arg should contain {"clear": True}
        data_arg = call_args[1].get("data") or (
            call_args[0][2] if len(call_args[0]) > 2 else None
        )
        assert data_arg == {"clear": True}
