# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestQueueHistory:
    """Test prompt history retrieval."""

    def test_get_history(self):
        """Should format history entries with outputs."""
        mock_response = {
            "abc-123": {
                "outputs": {
                    "9": {
                        "images": [
                            {
                                "filename": "ComfyUI_00001_.png",
                                "subfolder": "",
                                "type": "output",
                            }
                        ]
                    }
                },
                "status": {"status_str": "success", "completed": True},
            }
        }
        with patch(
            "cli_anything.comfyui.core.queue.api_get", return_value=mock_response
        ):
            result = queue_mod.get_history("http://localhost:8188")

        assert result["total"] == 1
        assert "abc-123" in result["history"]
        entry = result["history"]["abc-123"]
        assert entry["completed"] is True
        assert len(entry["outputs"]) == 1
        assert entry["outputs"][0]["filename"] == "ComfyUI_00001_.png"

    def test_get_prompt_history_not_found(self):
        """Should raise RuntimeError when prompt ID not in history."""
        with patch("cli_anything.comfyui.core.queue.api_get", return_value={}):
            with pytest.raises(RuntimeError, match="not found"):
                queue_mod.get_prompt_history("http://localhost:8188", "nonexistent-id")

    def test_interrupt(self):
        """Should call interrupt endpoint and return status."""
        with patch("cli_anything.comfyui.core.queue.api_post", return_value={}):
            result = queue_mod.interrupt("http://localhost:8188")
        assert result["status"] == "interrupted"
