# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIWorkflow:
    """Test CLI workflow commands."""

    def test_workflow_list(self, runner, tmp_path, sample_workflow):
        """workflow list should display JSON files."""
        (tmp_path / "my_wf.json").write_text(json.dumps(sample_workflow))

        result = runner.invoke(cli, ["workflow", "list", str(tmp_path)])
        assert result.exit_code == 0
        assert "my_wf.json" in result.output

    def test_workflow_validate_valid(self, runner, workflow_file):
        """workflow validate should pass for a valid workflow."""
        result = runner.invoke(cli, ["workflow", "validate", workflow_file])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_workflow_validate_json_output(self, runner, workflow_file):
        """--json flag should produce valid JSON output."""
        result = runner.invoke(cli, ["--json", "workflow", "validate", workflow_file])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "valid" in data
        assert "node_count" in data


class TestCLIQueue:
    """Test CLI queue commands."""

    def test_queue_prompt(self, runner, workflow_file):
        """queue prompt should queue a workflow and show prompt_id."""
        mock_response = {"prompt_id": "test-id-999", "number": 0, "node_errors": {}}
        with patch(
            "cli_anything.comfyui.core.queue.api_post", return_value=mock_response
        ):
            result = runner.invoke(
                cli, ["queue", "prompt", "--workflow", workflow_file]
            )

        assert result.exit_code == 0
        assert "test-id-999" in result.output

    def test_queue_status(self, runner):
        """queue status should show running and pending counts."""
        mock_response = {"queue_running": [], "queue_pending": [["id1", {}, {}, {}]]}
        with patch(
            "cli_anything.comfyui.core.queue.api_get", return_value=mock_response
        ):
            result = runner.invoke(cli, ["queue", "status"])

        assert result.exit_code == 0
        assert "1" in result.output

    def test_queue_clear_with_confirm(self, runner):
        """queue clear --confirm should skip prompt and clear."""
        with patch("cli_anything.comfyui.core.queue.api_delete", return_value={}):
            result = runner.invoke(cli, ["queue", "clear", "--confirm"])

        assert result.exit_code == 0
        assert "cleared" in result.output

    def test_queue_history_json(self, runner):
        """queue history --json should return valid JSON."""
        mock_response = {
            "abc": {
                "outputs": {},
                "status": {"status_str": "success", "completed": True},
            }
        }
        with patch(
            "cli_anything.comfyui.core.queue.api_get", return_value=mock_response
        ):
            result = runner.invoke(cli, ["--json", "queue", "history"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "history" in data
        assert "total" in data


class TestCLIModels:
    """Test CLI models commands."""

    def test_models_checkpoints(self, runner):
        """models checkpoints should list checkpoint names."""
        mock_resp = {
            "CheckpointLoaderSimple": {
                "input": {
                    "required": {
                        "ckpt_name": [
                            ["v1-5-pruned-emaonly.ckpt", "sd_xl_base_1.0.safetensors"],
                            {},
                        ]
                    }
                }
            }
        }
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = runner.invoke(cli, ["models", "checkpoints"])

        assert result.exit_code == 0
        assert "v1-5-pruned-emaonly.ckpt" in result.output

    def test_models_checkpoints_json(self, runner):
        """models checkpoints --json should return a JSON array."""
        mock_resp = {
            "CheckpointLoaderSimple": {
                "input": {"required": {"ckpt_name": [["model_a.safetensors"], {}]}}
            }
        }
        with patch("cli_anything.comfyui.core.models.api_get", return_value=mock_resp):
            result = runner.invoke(cli, ["--json", "models", "checkpoints"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert "model_a.safetensors" in data
