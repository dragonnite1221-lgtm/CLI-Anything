# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestEffects:
    def _make_project_with_track(self):
        proj = create_project()
        add_track(proj, name="FX Track")
        return proj

    def test_list_available(self):
        effects = list_available()
        assert len(effects) > 10
        names = [e["name"] for e in effects]
        assert "amplify" in names
        assert "normalize" in names
        assert "echo" in names

    def test_list_available_by_category(self):
        effects = list_available("volume")
        assert all(e["category"] == "volume" for e in effects)
        assert len(effects) >= 2

    def test_get_effect_info(self):
        info = get_effect_info("amplify")
        assert info["name"] == "amplify"
        assert "gain_db" in info["params"]

    def test_get_effect_info_unknown(self):
        with pytest.raises(ValueError, match="Unknown effect"):
            get_effect_info("nonexistent_effect")

    def test_validate_params_defaults(self):
        result = validate_params("amplify", {})
        assert result["gain_db"] == 0.0

    def test_validate_params_custom(self):
        result = validate_params("amplify", {"gain_db": 6.0})
        assert result["gain_db"] == 6.0

    def test_validate_params_out_of_range(self):
        with pytest.raises(ValueError, match="maximum"):
            validate_params("amplify", {"gain_db": 100.0})

    def test_validate_params_unknown(self):
        with pytest.raises(ValueError, match="Unknown parameters"):
            validate_params("amplify", {"unknown_param": 5})

    def test_add_effect(self):
        proj = self._make_project_with_track()
        result = add_effect(proj, "normalize", 0, {"target_db": -3.0})
        assert result["name"] == "normalize"
        assert result["params"]["target_db"] == -3.0
        assert len(proj["tracks"][0]["effects"]) == 1

    def test_add_effect_unknown(self):
        proj = self._make_project_with_track()
        with pytest.raises(ValueError, match="Unknown effect"):
            add_effect(proj, "nonexistent", 0)

    def test_add_effect_out_of_range(self):
        proj = self._make_project_with_track()
        with pytest.raises(IndexError):
            add_effect(proj, "amplify", 5)

    def test_remove_effect(self):
        proj = self._make_project_with_track()
        add_effect(proj, "amplify", 0, {"gain_db": 3.0})
        removed = remove_effect(proj, 0, 0)
        assert removed["name"] == "amplify"
        assert len(proj["tracks"][0]["effects"]) == 0

    def test_remove_effect_out_of_range(self):
        proj = self._make_project_with_track()
        with pytest.raises(IndexError):
            remove_effect(proj, 0, 0)

    def test_set_effect_param(self):
        proj = self._make_project_with_track()
        add_effect(proj, "echo", 0, {"delay_ms": 300, "decay": 0.4})
        set_effect_param(proj, 0, "delay_ms", 600.0, 0)
        assert proj["tracks"][0]["effects"][0]["params"]["delay_ms"] == 600.0

    def test_set_effect_param_unknown(self):
        proj = self._make_project_with_track()
        add_effect(proj, "amplify", 0)
        with pytest.raises(ValueError, match="Unknown parameter"):
            set_effect_param(proj, 0, "fake_param", 5.0, 0)

    def test_list_effects(self):
        proj = self._make_project_with_track()
        add_effect(proj, "normalize", 0)
        add_effect(proj, "compress", 0)
        effects = list_effects(proj, 0)
        assert len(effects) == 2
        assert effects[0]["name"] == "normalize"
        assert effects[1]["name"] == "compress"

    def test_all_effects_have_valid_params(self):
        """Ensure every effect in the registry has valid param specs."""
        for name, info in EFFECT_REGISTRY.items():
            assert "params" in info, f"Effect {name} missing params"
            assert "category" in info, f"Effect {name} missing category"
            assert "description" in info, f"Effect {name} missing description"
            # Validate defaults pass validation
            result = validate_params(name, {})
            assert isinstance(result, dict)
