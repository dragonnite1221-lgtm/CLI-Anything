# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestModifiers:
    def _make_scene_with_object(self):
        proj = create_scene()
        add_object(proj, name="Cube")
        return proj

    def test_list_available(self):
        mods = list_available()
        assert len(mods) >= 8
        names = [m["name"] for m in mods]
        assert "subdivision_surface" in names
        assert "mirror" in names
        assert "array" in names

    def test_list_by_category(self):
        gen = list_available(category="generate")
        assert all(m["category"] == "generate" for m in gen)
        assert len(gen) >= 5

    def test_get_modifier_info(self):
        info = get_modifier_info("subdivision_surface")
        assert info["name"] == "subdivision_surface"
        assert "levels" in info["params"]

    def test_get_modifier_info_unknown(self):
        with pytest.raises(ValueError, match="Unknown modifier"):
            get_modifier_info("nonexistent")

    def test_validate_params(self):
        params = validate_params("subdivision_surface", {"levels": 3})
        assert params["levels"] == 3
        assert params["render_levels"] == 2  # default

    def test_validate_params_defaults(self):
        params = validate_params("subdivision_surface", {})
        assert params["levels"] == 1

    def test_validate_params_out_of_range(self):
        with pytest.raises(ValueError, match="maximum"):
            validate_params("subdivision_surface", {"levels": 10})

    def test_validate_params_unknown(self):
        with pytest.raises(ValueError, match="Unknown parameters"):
            validate_params("subdivision_surface", {"bogus": 1})

    def test_add_modifier(self):
        proj = self._make_scene_with_object()
        result = add_modifier(proj, "subdivision_surface", 0, params={"levels": 2})
        assert result["type"] == "subdivision_surface"
        assert result["params"]["levels"] == 2
        assert len(proj["objects"][0]["modifiers"]) == 1

    def test_add_modifier_invalid_object(self):
        proj = self._make_scene_with_object()
        with pytest.raises(IndexError):
            add_modifier(proj, "subdivision_surface", 5)

    def test_add_modifier_unknown(self):
        proj = self._make_scene_with_object()
        with pytest.raises(ValueError, match="Unknown modifier"):
            add_modifier(proj, "nonexistent", 0)

    def test_remove_modifier(self):
        proj = self._make_scene_with_object()
        add_modifier(proj, "subdivision_surface", 0)
        removed = remove_modifier(proj, 0, 0)
        assert removed["type"] == "subdivision_surface"
        assert len(proj["objects"][0]["modifiers"]) == 0

    def test_set_modifier_param(self):
        proj = self._make_scene_with_object()
        add_modifier(proj, "subdivision_surface", 0, params={"levels": 1})
        set_modifier_param(proj, 0, "levels", 3, 0)
        assert proj["objects"][0]["modifiers"][0]["params"]["levels"] == 3

    def test_set_modifier_param_invalid(self):
        proj = self._make_scene_with_object()
        add_modifier(proj, "subdivision_surface", 0)
        with pytest.raises(ValueError, match="Unknown parameter"):
            set_modifier_param(proj, 0, "bogus", 1, 0)

    def test_list_modifiers(self):
        proj = self._make_scene_with_object()
        add_modifier(proj, "subdivision_surface", 0)
        add_modifier(proj, "mirror", 0)
        result = list_modifiers(proj, 0)
        assert len(result) == 2
        assert result[0]["type"] == "subdivision_surface"
        assert result[1]["type"] == "mirror"

    def test_all_modifiers_have_valid_bpy_type(self):
        for name, spec in MODIFIER_REGISTRY.items():
            assert "bpy_type" in spec, f"Modifier '{name}' missing bpy_type"
            assert spec["bpy_type"], f"Modifier '{name}' has empty bpy_type"

    def test_array_modifier(self):
        proj = self._make_scene_with_object()
        result = add_modifier(proj, "array", 0, params={"count": 5})
        assert result["params"]["count"] == 5

    def test_bevel_modifier(self):
        proj = self._make_scene_with_object()
        result = add_modifier(proj, "bevel", 0, params={"width": 0.5, "segments": 3})
        assert result["params"]["width"] == 0.5
        assert result["params"]["segments"] == 3

    def test_solidify_modifier(self):
        proj = self._make_scene_with_object()
        result = add_modifier(proj, "solidify", 0, params={"thickness": 0.1})
        assert result["params"]["thickness"] == 0.1

    def test_boolean_modifier(self):
        proj = self._make_scene_with_object()
        result = add_modifier(proj, "boolean", 0, params={"operation": "UNION"})
        assert result["params"]["operation"] == "UNION"
