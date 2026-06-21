# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


@pytest.fixture
def test_project():
    """Create a test project and clean up after."""
    project_name = "test_e2e_project"

    # Create project
    result = run_cli_command(["project", "create", "--name", project_name])
    assert result["status"] == "success"

    yield project_name

    # Cleanup: Delete project (if implemented)
    try:
        run_cli_command(["project", "delete", "--name", project_name])
    except:
        pass


class TestProjectManagement:
    """Test project management commands."""

    def test_create_project(self):
        """Test creating a new project."""
        result = run_cli_command(["project", "create", "--name", "test_create"])
        assert result["status"] == "success"
        assert "created" in result["message"].lower()

    def test_list_projects(self):
        """Test listing all projects."""
        result = run_cli_command(["project", "list"])
        assert result["status"] == "success"
        assert isinstance(result["data"], list)

    def test_switch_project(self, test_project):
        """Test switching to a project."""
        result = run_cli_command(["project", "switch", "--name", test_project])
        assert result["status"] == "success"


class TestModelTraining:
    """Test model training functionality."""

    @pytest.mark.slow
    def test_train_classification(self, test_project, temp_csv_file):
        """Test training a classification model."""
        result = run_cli_command(
            [
                "train",
                "--data-path",
                temp_csv_file,
                "--target-col",
                "target",
                "--task-type",
                "classification",
                "--epochs",
                "2",  # Small for testing
                "--learning-rate",
                "0.0001",
            ]
        )

        assert result["status"] == "success"
        assert "model_id" in result["data"]
        assert "performance" in result["data"]

    @pytest.mark.slow
    def test_train_regression(self, test_project, temp_csv_file):
        """Test training a regression model."""
        result = run_cli_command(
            [
                "train",
                "--data-path",
                temp_csv_file,
                "--target-col",
                "target",
                "--task-type",
                "regression",
                "--epochs",
                "2",
                "--learning-rate",
                "0.0001",
            ]
        )

        assert result["status"] == "success"
        assert "model_id" in result["data"]


class TestModelManagement:
    """Test model management commands."""

    def test_list_models(self, test_project):
        """Test listing all models."""
        result = run_cli_command(["models", "list"])
        assert result["status"] == "success"
        assert isinstance(result["data"], list)

    def test_rank_models(self, test_project):
        """Test ranking models by performance."""
        result = run_cli_command(["models", "rank"])
        assert result["status"] == "success"
        assert isinstance(result["data"], list)


class TestStorageManagement:
    """Test storage management commands."""

    def test_storage_analyze(self, test_project):
        """Test storage analysis."""
        result = run_cli_command(["storage", "analyze"])
        assert result["status"] == "success"
        assert "total_size" in result["data"]
        assert "model_count" in result["data"]


class TestPrediction:
    """Test prediction functionality."""

    @pytest.mark.slow
    def test_predict(self, test_project, temp_csv_file):
        """Test making predictions with a trained model."""
        # First train a model
        train_result = run_cli_command(
            [
                "train",
                "--data-path",
                temp_csv_file,
                "--target-col",
                "target",
                "--task-type",
                "classification",
                "--epochs",
                "2",
            ]
        )

        assert train_result["status"] == "success"
        model_id = train_result["data"]["model_id"]

        # Now make predictions
        pred_result = run_cli_command(
            ["predict", "--model-id", model_id, "--data-path", temp_csv_file]
        )

        assert pred_result["status"] == "success"
        assert "predictions" in pred_result["data"]
        assert len(pred_result["data"]["predictions"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
