# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestModelDiscovery:
    """Test model listing as part of setup workflow."""

    def test_discover_all_model_types(self, runner):
        """Should list all four model types without error."""
        ckpt_resp = {
            "CheckpointLoaderSimple": {
                "input": {"required": {"ckpt_name": [["model_a.ckpt"], {}]}}
            }
        }
        lora_resp = {
            "LoraLoader": {
                "input": {"required": {"lora_name": [["lora_style.safetensors"], {}]}}
            }
        }
        vae_resp = {
            "VAELoader": {"input": {"required": {"vae_name": [["vae.ckpt"], {}]}}}
        }
        cn_resp = {
            "ControlNetLoader": {
                "input": {"required": {"control_net_name": [["canny.pth"], {}]}}
            }
        }

        with patch("cli_anything.comfyui.core.models.api_get") as mock_api:
            mock_api.side_effect = [ckpt_resp, lora_resp, vae_resp, cn_resp]

            for cmd in [
                ["models", "checkpoints"],
                ["models", "loras"],
                ["models", "vaes"],
                ["models", "controlnets"],
            ]:
                result = runner.invoke(cli, cmd)
                assert result.exit_code == 0, f"Failed on: {cmd} — {result.output}"


class TestErrorHandling:
    """Test error scenarios are handled gracefully."""

    def test_connection_refused_shows_error(self, runner, workflow_file):
        """Should show friendly error when ComfyUI is not running."""
        with patch(
            "cli_anything.comfyui.core.queue.api_post",
            side_effect=RuntimeError(
                "Cannot connect to ComfyUI at http://localhost:8188. Is ComfyUI running?"
            ),
        ):
            result = runner.invoke(
                cli, ["queue", "prompt", "--workflow", workflow_file]
            )

        assert result.exit_code != 0
        assert "Cannot connect" in result.output or "Error" in result.output

    def test_server_rejects_workflow_shows_error(self, runner, workflow_file):
        """Should show error message when server rejects the workflow."""
        with patch(
            "cli_anything.comfyui.core.queue.api_post",
            return_value={
                "error": {"message": "Node not found: BadNode", "type": "value_error"}
            },
        ):
            result = runner.invoke(
                cli, ["queue", "prompt", "--workflow", workflow_file]
            )

        assert result.exit_code != 0
        assert "Error" in result.output or "rejected" in result.output

    def test_nonexistent_workflow_shows_error(self, runner):
        """Should error when workflow file does not exist."""
        result = runner.invoke(
            cli, ["queue", "prompt", "--workflow", "/nonexistent.json"]
        )
        assert result.exit_code != 0

    def test_download_missing_image_shows_error(self, runner, tmp_path):
        """Should error when trying to download non-existent image."""
        with patch(
            "cli_anything.comfyui.core.images.api_get_raw",
            side_effect=RuntimeError("ComfyUI API error 404"),
        ):
            result = runner.invoke(
                cli,
                [
                    "images",
                    "download",
                    "--filename",
                    "nonexistent.png",
                    "--output",
                    str(tmp_path / "out.png"),
                ],
            )

        assert result.exit_code != 0
