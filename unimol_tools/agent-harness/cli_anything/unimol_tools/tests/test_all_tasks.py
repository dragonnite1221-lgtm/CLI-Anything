# ruff: noqa: F403, F405, E501
from .test_all_tasks_helpers import *  # noqa: F403


class TestBinaryClassification:
    """Test binary classification workflow"""

    def test_binary_classification_project(self, tmp_dir, binary_classification_data):
        """Test complete binary classification workflow"""
        from cli_anything.unimol_tools.core import project as project_mod

        # Create project
        result = project_mod.create_project(
            name="binary_test",
            task="classification",
            output_dir=tmp_dir,
            model_name="unimolv1",
        )

        assert result["status"] == "created"
        assert os.path.exists(result["project_path"])

        project_path = result["project_path"]

        # Load and verify project
        load_result = project_mod.load_project(project_path)
        project = load_result["project"]

        assert project["project_type"] == "classification"
        assert project["config"]["task"] == "classification"
        assert project["config"]["metrics"] == "auc"

        # Set training dataset
        set_result = project_mod.set_dataset(
            project, "train", binary_classification_data["train"]
        )

        assert set_result["status"] == "updated"
        assert set_result["dataset_type"] == "train"

        # Save project
        project_mod.save_project(project_path, project)

        # Verify datasets are set
        load_result = project_mod.load_project(project_path)
        project = load_result["project"]
        assert project["datasets"]["train"] is not None


class TestRegression:
    """Test regression workflow"""

    def test_regression_project(self, tmp_dir, regression_data):
        """Test complete regression workflow"""
        from cli_anything.unimol_tools.core import project as project_mod

        # Create regression project
        result = project_mod.create_project(
            name="regression_test",
            task="regression",
            output_dir=tmp_dir,
            model_name="unimolv1",
        )

        assert result["status"] == "created"
        project_path = result["project_path"]

        # Load project
        load_result = project_mod.load_project(project_path)
        project = load_result["project"]

        assert project["project_type"] == "regression"
        assert project["config"]["task"] == "regression"
        assert project["config"]["metrics"] == "mae"

        # Set datasets
        set_result = project_mod.set_dataset(project, "train", regression_data["train"])

        assert set_result["status"] == "updated"
        project_mod.save_project(project_path, project)

        # Set test dataset
        load_result = project_mod.load_project(project_path)
        project = load_result["project"]

        set_result = project_mod.set_dataset(project, "test", regression_data["test"])

        assert set_result["status"] == "updated"
        project_mod.save_project(project_path, project)

        # Verify both datasets are set
        load_result = project_mod.load_project(project_path)
        project = load_result["project"]
        assert project["datasets"]["train"] is not None
        assert project["datasets"]["test"] is not None
