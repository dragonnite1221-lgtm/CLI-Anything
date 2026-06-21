# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestWorkflowLoad:
    """Test workflow file loading."""

    def test_load_valid_workflow(self, workflow_file, sample_workflow):
        """Should load a valid workflow JSON file."""
        result = workflow_mod.load_workflow(workflow_file)
        assert result == sample_workflow
        assert "3" in result

    def test_load_nonexistent_file(self):
        """Should raise RuntimeError for missing file."""
        with pytest.raises(RuntimeError, match="not found"):
            workflow_mod.load_workflow("/nonexistent/path/workflow.json")

    def test_load_non_json_extension(self, tmp_path):
        """Should raise RuntimeError for non-.json file."""
        p = tmp_path / "workflow.txt"
        p.write_text("{}")
        with pytest.raises(RuntimeError, match=".json"):
            workflow_mod.load_workflow(str(p))

    def test_load_invalid_json(self, tmp_path):
        """Should raise RuntimeError for malformed JSON."""
        p = tmp_path / "bad.json"
        p.write_text("{not valid json")
        with pytest.raises(RuntimeError, match="Invalid JSON"):
            workflow_mod.load_workflow(str(p))

    def test_load_non_dict_json(self, tmp_path):
        """Should raise RuntimeError if JSON root is not a dict."""
        p = tmp_path / "list.json"
        p.write_text("[1, 2, 3]")
        with pytest.raises(RuntimeError, match="JSON object"):
            workflow_mod.load_workflow(str(p))


class TestWorkflowSave:
    """Test workflow file saving."""

    def test_save_workflow(self, tmp_path, sample_workflow):
        """Should save workflow to JSON file."""
        dest = str(tmp_path / "saved.json")
        result = workflow_mod.save_workflow(sample_workflow, dest)
        assert result["status"] == "saved"
        assert result["node_count"] == len(sample_workflow)
        assert Path(dest).exists()
        loaded = json.loads(Path(dest).read_text())
        assert loaded == sample_workflow

    def test_save_creates_parent_dirs(self, tmp_path, sample_workflow):
        """Should create parent directories if they don't exist."""
        dest = str(tmp_path / "nested" / "deep" / "workflow.json")
        result = workflow_mod.save_workflow(sample_workflow, dest)
        assert result["status"] == "saved"
        assert Path(dest).exists()

    def test_save_non_dict_raises(self):
        """Should raise RuntimeError if workflow is not a dict."""
        with pytest.raises(RuntimeError, match="must be a dict"):
            workflow_mod.save_workflow([1, 2, 3], "/tmp/test.json")


class TestWorkflowList:
    """Test listing workflow files in a directory."""

    def test_list_workflows(self, tmp_path, sample_workflow):
        """Should list all JSON files in directory."""
        (tmp_path / "workflow1.json").write_text(json.dumps(sample_workflow))
        (tmp_path / "workflow2.json").write_text(
            json.dumps({"1": {"class_type": "SaveImage", "inputs": {}}})
        )
        (tmp_path / "not_json.txt").write_text("ignored")

        result = workflow_mod.list_workflows(str(tmp_path))
        assert len(result) == 2
        filenames = [r["filename"] for r in result]
        assert "workflow1.json" in filenames
        assert "workflow2.json" in filenames

    def test_list_empty_directory(self, tmp_path):
        """Should return empty list for directory with no JSON files."""
        result = workflow_mod.list_workflows(str(tmp_path))
        assert result == []

    def test_list_nonexistent_directory(self):
        """Should raise RuntimeError for nonexistent directory."""
        with pytest.raises(RuntimeError, match="not found"):
            workflow_mod.list_workflows("/nonexistent/dir/xyz")


class TestWorkflowValidate:
    """Test workflow validation."""

    def test_valid_workflow(self, sample_workflow):
        """Should pass validation for a well-formed workflow."""
        result = workflow_mod.validate_workflow(sample_workflow)
        assert result["valid"] is True
        assert result["node_count"] == len(sample_workflow)
        assert result["errors"] == []

    def test_empty_workflow(self):
        """Should warn about empty workflow but not fail."""
        result = workflow_mod.validate_workflow({})
        assert result["valid"] is True
        assert any("empty" in w.lower() for w in result["warnings"])

    def test_missing_class_type(self):
        """Should error on node missing class_type."""
        wf = {"1": {"inputs": {"text": "hello"}}}
        result = workflow_mod.validate_workflow(wf)
        assert result["valid"] is False
        assert any("class_type" in e for e in result["errors"])

    def test_non_dict_inputs(self):
        """Should error when inputs is not a dict."""
        wf = {"1": {"class_type": "CLIPTextEncode", "inputs": ["bad"]}}
        result = workflow_mod.validate_workflow(wf)
        assert result["valid"] is False

    def test_non_dict_workflow(self):
        """Should fail validation if workflow is not a dict."""
        result = workflow_mod.validate_workflow("not a dict")
        assert result["valid"] is False
        assert result["node_count"] == 0
