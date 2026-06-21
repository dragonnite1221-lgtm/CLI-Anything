# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestFullGenerationWorkflow:
    """Simulate complete generate -> check -> download workflow."""

    def test_queue_and_check_status(self, runner, workflow_file):
        """Full flow: validate workflow -> queue it -> check queue status."""
        prompt_id = "e2e-prompt-001"

        queue_response = {"prompt_id": prompt_id, "number": 0, "node_errors": {}}
        status_response = {
            "queue_running": [["e2e-prompt-001", {}, {}, {}]],
            "queue_pending": [],
        }

        with (
            patch(
                "cli_anything.comfyui.core.queue.api_post", return_value=queue_response
            ),
            patch(
                "cli_anything.comfyui.core.queue.api_get", return_value=status_response
            ),
        ):
            # Step 1: Validate
            result = runner.invoke(cli, ["workflow", "validate", workflow_file])
            assert result.exit_code == 0

            # Step 2: Queue
            result = runner.invoke(
                cli, ["queue", "prompt", "--workflow", workflow_file]
            )
            assert result.exit_code == 0
            assert prompt_id in result.output

            # Step 3: Check status
            result = runner.invoke(cli, ["queue", "status"])
            assert result.exit_code == 0

    def test_queue_then_download(self, runner, workflow_file, tmp_path):
        """Full flow: queue -> list outputs -> download image."""
        prompt_id = "e2e-prompt-002"
        img_filename = "ComfyUI_00001_.png"
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 128

        history_response = {
            prompt_id: {
                "outputs": {
                    "9": {
                        "images": [
                            {
                                "filename": img_filename,
                                "subfolder": "",
                                "type": "output",
                            }
                        ]
                    }
                },
                "status": {"status_str": "success", "completed": True},
            }
        }

        dest = str(tmp_path / "downloaded.png")

        with (
            patch(
                "cli_anything.comfyui.core.queue.api_post",
                return_value={"prompt_id": prompt_id, "number": 0, "node_errors": {}},
            ),
            patch(
                "cli_anything.comfyui.core.queue.api_get", return_value=history_response
            ),
            patch(
                "cli_anything.comfyui.core.images.api_get_raw", return_value=fake_png
            ),
        ):
            # Queue
            result = runner.invoke(
                cli, ["queue", "prompt", "--workflow", workflow_file]
            )
            assert result.exit_code == 0

            # List outputs
            result = runner.invoke(cli, ["images", "list", "--prompt-id", prompt_id])
            assert result.exit_code == 0
            assert img_filename in result.output

            # Download
            result = runner.invoke(
                cli,
                [
                    "images",
                    "download",
                    "--filename",
                    img_filename,
                    "--output",
                    dest,
                ],
            )
            assert result.exit_code == 0
            assert Path(dest).read_bytes() == fake_png

    def test_json_mode_full_flow(self, runner, workflow_file):
        """All commands in --json mode should produce valid JSON throughout."""
        prompt_id = "e2e-json-003"
        queue_response = {"prompt_id": prompt_id, "number": 0, "node_errors": {}}

        with patch(
            "cli_anything.comfyui.core.queue.api_post", return_value=queue_response
        ):
            result = runner.invoke(
                cli, ["--json", "queue", "prompt", "--workflow", workflow_file]
            )
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["prompt_id"] == prompt_id

    def test_interrupt_generation(self, runner):
        """queue interrupt should stop current generation."""
        with patch("cli_anything.comfyui.core.queue.api_post", return_value={}):
            result = runner.invoke(cli, ["queue", "interrupt"])
        assert result.exit_code == 0
        assert "interrupted" in result.output

    def test_clear_queue_and_verify(self, runner):
        """Clear queue then verify it is empty."""
        empty_status = {"queue_running": [], "queue_pending": []}

        with (
            patch("cli_anything.comfyui.core.queue.api_delete", return_value={}),
            patch("cli_anything.comfyui.core.queue.api_get", return_value=empty_status),
        ):
            result = runner.invoke(cli, ["queue", "clear", "--confirm"])
            assert result.exit_code == 0
            assert "cleared" in result.output

            result = runner.invoke(cli, ["--json", "queue", "status"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["running_count"] == 0
            assert data["pending_count"] == 0
