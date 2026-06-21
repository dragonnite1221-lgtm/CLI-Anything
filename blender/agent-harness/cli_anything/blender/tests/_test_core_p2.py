# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class TestMaterials:
    def _make_scene(self):
        return create_scene()

    def test_create_material(self):
        proj = self._make_scene()
        mat = create_material(proj, name="Red")
        assert mat["name"] == "Red"
        assert mat["type"] == "principled"
        assert len(proj["materials"]) == 1

    def test_create_material_with_color(self):
        proj = self._make_scene()
        mat = create_material(proj, color=[1.0, 0.0, 0.0, 1.0])
        assert mat["color"] == [1.0, 0.0, 0.0, 1.0]

    def test_create_material_3_component_color(self):
        proj = self._make_scene()
        mat = create_material(proj, color=[1.0, 0.0, 0.0])
        assert mat["color"] == [1.0, 0.0, 0.0, 1.0]

    def test_create_material_invalid_color(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="must be 0.0-1.0"):
            create_material(proj, color=[2.0, 0.0, 0.0, 1.0])

    def test_create_material_invalid_metallic(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Metallic must be"):
            create_material(proj, metallic=1.5)

    def test_create_material_invalid_roughness(self):
        proj = self._make_scene()
        with pytest.raises(ValueError, match="Roughness must be"):
            create_material(proj, roughness=-0.1)

    def test_unique_material_names(self):
        proj = self._make_scene()
        m1 = create_material(proj, name="Mat")
        m2 = create_material(proj, name="Mat")
        assert m1["name"] != m2["name"]

    def test_assign_material(self):
        proj = self._make_scene()
        mat = create_material(proj, name="Metal")
        add_object(proj, name="Cube")
        result = assign_material(proj, 0, 0)
        assert result["material"] == "Metal"
        assert proj["objects"][0]["material"] == mat["id"]

    def test_assign_material_invalid_indices(self):
        proj = self._make_scene()
        with pytest.raises(IndexError):
            assign_material(proj, 0, 0)

    def test_set_material_property_metallic(self):
        proj = self._make_scene()
        create_material(proj)
        set_material_property(proj, 0, "metallic", 1.0)
        assert proj["materials"][0]["metallic"] == 1.0

    def test_set_material_property_roughness(self):
        proj = self._make_scene()
        create_material(proj)
        set_material_property(proj, 0, "roughness", 0.1)
        assert proj["materials"][0]["roughness"] == 0.1

    def test_set_material_property_color(self):
        proj = self._make_scene()
        create_material(proj)
        set_material_property(proj, 0, "color", [1.0, 0.0, 0.0, 1.0])
        assert proj["materials"][0]["color"] == [1.0, 0.0, 0.0, 1.0]

    def test_set_material_property_invalid(self):
        proj = self._make_scene()
        create_material(proj)
        with pytest.raises(ValueError, match="Unknown material property"):
            set_material_property(proj, 0, "bogus", 1.0)

    def test_set_material_property_out_of_range(self):
        proj = self._make_scene()
        create_material(proj)
        with pytest.raises(ValueError, match="maximum"):
            set_material_property(proj, 0, "metallic", 2.0)

    def test_list_materials(self):
        proj = self._make_scene()
        create_material(proj, name="A")
        create_material(proj, name="B")
        result = list_materials(proj)
        assert len(result) == 2

    def test_get_material(self):
        proj = self._make_scene()
        create_material(proj, name="Test")
        mat = get_material(proj, 0)
        assert mat["name"] == "Test"
