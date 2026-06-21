# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCliLayerSet:
    def test_layer_set_accepts_negative_offsets(self, tmp_path):
        proj = create_project()
        add_layer(proj, name="Overlay")
        project_path = tmp_path / "negative-offsets.gimp-cli.json"
        save_project(proj, str(project_path))

        gimp_cli._session = None
        runner = CliRunner()
        result = runner.invoke(
            gimp_cli.cli,
            ["--project", str(project_path), "layer", "set", "0", "offset_x", "-48"],
        )
        assert result.exit_code == 0, result.output

        updated = open_project(str(project_path))
        assert updated["layers"][0]["offset_x"] == -48


class TestFilters:
    def _make_project_with_layer(self):
        proj = create_project()
        add_layer(proj, name="Test")
        return proj

    def test_list_available(self):
        filters = list_available()
        assert len(filters) > 10
        names = [f["name"] for f in filters]
        assert "brightness" in names
        assert "gaussian_blur" in names

    def test_list_by_category(self):
        blurs = list_available(category="blur")
        assert all(f["category"] == "blur" for f in blurs)
        assert len(blurs) >= 3

    def test_get_filter_info(self):
        info = get_filter_info("brightness")
        assert info["name"] == "brightness"
        assert "factor" in info["params"]

    def test_get_filter_info_unknown(self):
        with pytest.raises(ValueError, match="Unknown filter"):
            get_filter_info("nonexistent")

    def test_validate_params(self):
        params = validate_params("brightness", {"factor": 1.5})
        assert params["factor"] == 1.5

    def test_validate_params_defaults(self):
        params = validate_params("brightness", {})
        assert params["factor"] == 1.0

    def test_validate_params_out_of_range(self):
        with pytest.raises(ValueError, match="maximum"):
            validate_params("brightness", {"factor": 100.0})

    def test_validate_params_unknown(self):
        with pytest.raises(ValueError, match="Unknown parameters"):
            validate_params("brightness", {"bogus": 1.0})

    def test_add_filter(self):
        proj = self._make_project_with_layer()
        result = add_filter(proj, "brightness", 0, {"factor": 1.2})
        assert result["name"] == "brightness"
        assert proj["layers"][0]["filters"][0]["name"] == "brightness"

    def test_add_filter_invalid_layer(self):
        proj = self._make_project_with_layer()
        with pytest.raises(IndexError):
            add_filter(proj, "brightness", 5, {})

    def test_add_filter_unknown(self):
        proj = self._make_project_with_layer()
        with pytest.raises(ValueError, match="Unknown filter"):
            add_filter(proj, "nonexistent", 0, {})

    def test_remove_filter(self):
        proj = self._make_project_with_layer()
        add_filter(proj, "brightness", 0, {"factor": 1.2})
        removed = remove_filter(proj, 0, 0)
        assert removed["name"] == "brightness"
        assert len(proj["layers"][0]["filters"]) == 0

    def test_set_filter_param(self):
        proj = self._make_project_with_layer()
        add_filter(proj, "brightness", 0, {"factor": 1.0})
        set_filter_param(proj, 0, "factor", 1.5, 0)
        assert proj["layers"][0]["filters"][0]["params"]["factor"] == 1.5

    def test_list_filters(self):
        proj = self._make_project_with_layer()
        add_filter(proj, "brightness", 0, {"factor": 1.2})
        add_filter(proj, "contrast", 0, {"factor": 1.1})
        result = list_filters(proj, 0)
        assert len(result) == 2
        assert result[0]["name"] == "brightness"
        assert result[1]["name"] == "contrast"

    def test_all_filters_have_valid_engine(self):
        valid_engines = {
            "pillow_enhance",
            "pillow_ops",
            "pillow_filter",
            "pillow_transform",
            "custom",
        }
        for name, spec in FILTER_REGISTRY.items():
            assert spec["engine"] in valid_engines, (
                f"Filter '{name}' has invalid engine"
            )
