# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestModels:
    """Test model listing functions."""

    def _make_checkpoint_response(self, names):
        return {
            "CheckpointLoaderSimple": {
                "input": {"required": {"ckpt_name": [names, {}]}}
            }
        }

    def _make_lora_response(self, names):
        return {"LoraLoader": {"input": {"required": {"lora_name": [names, {}]}}}}

    def _make_vae_response(self, names):
        return {"VAELoader": {"input": {"required": {"vae_name": [names, {}]}}}}

    def _make_controlnet_response(self, names):
        return {
            "ControlNetLoader": {
                "input": {"required": {"control_net_name": [names, {}]}}
            }
        }

    def test_list_checkpoints(self):
        """Should return sorted list of checkpoint names."""
        mock_resp = self._make_checkpoint_response(
            [
                "sd_xl_base_1.0.safetensors",
                "v1-5-pruned-emaonly.ckpt",
                "deliberate_v2.safetensors",
            ]
        )
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.list_checkpoints("http://localhost:8188")

        assert isinstance(result, list)
        assert len(result) == 3
        assert result == sorted(result)

    def test_list_loras(self):
        """Should return sorted list of LoRA names."""
        mock_resp = self._make_lora_response(
            ["lora_b.safetensors", "lora_a.safetensors"]
        )
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.list_loras("http://localhost:8188")

        assert result == ["lora_a.safetensors", "lora_b.safetensors"]

    def test_list_vaes(self):
        """Should return sorted list of VAE names."""
        mock_resp = self._make_vae_response(["vae-ft-mse-840000-ema-pruned.ckpt"])
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.list_vaes("http://localhost:8188")

        assert "vae-ft-mse-840000-ema-pruned.ckpt" in result

    def test_list_controlnets(self):
        """Should return sorted list of ControlNet names."""
        mock_resp = self._make_controlnet_response(["control_v11p_sd15_canny.pth"])
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.list_controlnets("http://localhost:8188")

        assert "control_v11p_sd15_canny.pth" in result

    def test_list_checkpoints_bad_response_raises(self):
        """Should raise RuntimeError on unexpected API response."""
        with patch("cli_anything.comfyui.core.models.api_get", return_value={}):
            with pytest.raises(RuntimeError, match="checkpoint"):
                models_mod.list_checkpoints("http://localhost:8188")

    def test_get_node_info(self):
        """Should return formatted node schema."""
        mock_resp = {
            "KSampler": {
                "display_name": "KSampler",
                "description": "Samples latents",
                "category": "sampling",
                "input": {"required": {"steps": [["INT"], {"default": 20}]}},
                "output": ["LATENT"],
                "output_name": ["LATENT"],
            }
        }
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.get_node_info("http://localhost:8188", "KSampler")

        assert result["class_type"] == "KSampler"
        assert result["category"] == "sampling"

    def test_get_node_info_not_found_raises(self):
        """Should raise RuntimeError when node class not in response."""
        with patch("cli_anything.comfyui.core.models.api_get", return_value={}):
            with pytest.raises(RuntimeError, match="not found"):
                models_mod.get_node_info("http://localhost:8188", "NonExistentNode")

    def test_list_all_node_classes(self):
        """Should return sorted list of all node class names."""
        mock_resp = {"KSampler": {}, "CLIPTextEncode": {}, "SaveImage": {}}
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = models_mod.list_all_node_classes("http://localhost:8188")

        assert result == ["CLIPTextEncode", "KSampler", "SaveImage"]
