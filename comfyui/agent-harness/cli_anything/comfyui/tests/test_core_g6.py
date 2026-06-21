# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIImages:
    """Test CLI images commands."""

    def test_images_list(self, runner):
        """images list should show output filenames."""
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
            result = runner.invoke(cli, ["images", "list", "--prompt-id", "abc-123"])

        assert result.exit_code == 0
        assert "ComfyUI_00001_.png" in result.output

    def test_images_download(self, runner, tmp_path):
        """images download should save file to disk."""
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30
        dest = str(tmp_path / "out.png")

        with patch(
            "cli_anything.comfyui.core.images.api_get_raw", return_value=fake_png
        ):
            result = runner.invoke(
                cli,
                [
                    "images",
                    "download",
                    "--filename",
                    "ComfyUI_00001_.png",
                    "--output",
                    dest,
                ],
            )

        assert result.exit_code == 0
        assert "downloaded" in result.output.lower()
        assert Path(dest).exists()


class TestCLISystem:
    """Test CLI system commands."""

    def test_system_stats(self, runner):
        """system stats should display server info."""
        mock_stats = {
            "system": {"os": "linux", "python_version": "3.11"},
            "devices": [{"name": "NVIDIA RTX 3060", "vram_total": 12884901888}],
        }
        with patch("cli_anything.comfyui.comfyui_cli.api_get", return_value=mock_stats):
            result = runner.invoke(cli, ["system", "stats"])

        assert result.exit_code == 0

    def test_system_stats_json(self, runner):
        """system stats --json should return valid JSON."""
        mock_stats = {"system": {"os": "linux"}, "devices": []}
        with patch("cli_anything.comfyui.comfyui_cli.api_get", return_value=mock_stats):
            result = runner.invoke(cli, ["--json", "system", "stats"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "system" in data
