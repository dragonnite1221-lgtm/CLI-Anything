# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestImages:
    """Test image listing and downloading."""

    def test_list_output_images(self):
        """Should return list of image file refs for a prompt."""
        mock_history = {
            "prompt_id": "abc-123",
            "status": "success",
            "completed": True,
            "outputs": [
                {
                    "node_id": "9",
                    "filename": "ComfyUI_00001_.png",
                    "subfolder": "",
                    "type": "output",
                }
            ],
        }
        with patch(
            "cli_anything.comfyui.core.images.get_prompt_history",
            return_value=mock_history,
        ):
            result = images_mod.list_output_images("http://localhost:8188", "abc-123")

        assert len(result) == 1
        assert result[0]["filename"] == "ComfyUI_00001_.png"

    def test_list_output_images_incomplete_raises(self):
        """Should raise RuntimeError when prompt not yet complete."""
        mock_history = {
            "prompt_id": "abc-123",
            "status": "running",
            "completed": False,
            "outputs": [],
        }
        with patch(
            "cli_anything.comfyui.core.images.get_prompt_history",
            return_value=mock_history,
        ):
            with pytest.raises(RuntimeError, match="not completed"):
                images_mod.list_output_images("http://localhost:8188", "abc-123")

    def test_download_image(self, tmp_path):
        """Should download image bytes and write to disk."""
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        dest = str(tmp_path / "output.png")

        with patch(
            "cli_anything.comfyui.core.images.api_get_raw", return_value=fake_png
        ):
            result = images_mod.download_image(
                base_url="http://localhost:8188",
                filename="ComfyUI_00001_.png",
                output_path=dest,
            )

        assert result["status"] == "downloaded"
        assert result["size_bytes"] == len(fake_png)
        assert Path(dest).read_bytes() == fake_png

    def test_download_image_no_overwrite_raises(self, tmp_path):
        """Should raise RuntimeError when output file exists and overwrite=False."""
        dest = tmp_path / "existing.png"
        dest.write_bytes(b"existing content")

        with pytest.raises(RuntimeError, match="already exists"):
            images_mod.download_image(
                base_url="http://localhost:8188",
                filename="ComfyUI_00001_.png",
                output_path=str(dest),
                overwrite=False,
            )

    def test_download_image_overwrite(self, tmp_path):
        """Should overwrite existing file when overwrite=True."""
        dest = tmp_path / "existing.png"
        dest.write_bytes(b"old content")
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50

        with patch(
            "cli_anything.comfyui.core.images.api_get_raw", return_value=fake_png
        ):
            images_mod.download_image(
                base_url="http://localhost:8188",
                filename="ComfyUI_00001_.png",
                output_path=str(dest),
                overwrite=True,
            )

        assert dest.read_bytes() == fake_png

    def test_download_prompt_images(self, tmp_path):
        """Should download all images for a prompt to a directory."""
        mock_history = {
            "prompt_id": "abc-123",
            "status": "success",
            "completed": True,
            "outputs": [
                {
                    "node_id": "9",
                    "filename": "ComfyUI_00001_.png",
                    "subfolder": "",
                    "type": "output",
                },
                {
                    "node_id": "9",
                    "filename": "ComfyUI_00002_.png",
                    "subfolder": "",
                    "type": "output",
                },
            ],
        }
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

        with (
            patch(
                "cli_anything.comfyui.core.images.get_prompt_history",
                return_value=mock_history,
            ),
            patch(
                "cli_anything.comfyui.core.images.api_get_raw", return_value=fake_png
            ),
        ):
            results = images_mod.download_prompt_images(
                base_url="http://localhost:8188",
                prompt_id="abc-123",
                output_dir=str(tmp_path),
            )

        assert len(results) == 2
        assert all(r["status"] == "downloaded" for r in results)
