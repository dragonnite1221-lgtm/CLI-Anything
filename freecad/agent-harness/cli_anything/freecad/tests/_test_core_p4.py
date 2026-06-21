# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403
from ._test_core_p0 import _make_project  # noqa: F401,E501


class TestMaterials:
    """Tests for the materials module."""

    def test_create_default(self):
        proj = _make_project()
        mat = create_material(proj)
        assert mat["name"] == "Material"
        assert mat["preset"] is None
        assert mat["color"] == [0.8, 0.8, 0.8, 1.0]
        assert mat["metallic"] == 0.0
        assert mat["roughness"] == 0.5
        assert mat["assigned_to"] == []
        assert len(proj["materials"]) == 1

    def test_create_from_preset(self):
        proj = _make_project()
        mat = create_material(proj, preset="steel")
        assert mat["preset"] == "steel"
        assert mat["color"] == PRESETS["steel"]["color"]
        assert mat["metallic"] == PRESETS["steel"]["metallic"]
        assert mat["roughness"] == PRESETS["steel"]["roughness"]
        # Name is derived from preset key
        assert mat["name"] == "Steel"

        with pytest.raises(ValueError, match="Unknown preset"):
            create_material(proj, preset="unobtanium")

    def test_create_with_color(self):
        proj = _make_project()
        mat = create_material(proj, name="Red", color=[1.0, 0.0, 0.0])
        # 3-component color gets alpha appended
        assert mat["color"] == [1.0, 0.0, 0.0, 1.0]

        mat2 = create_material(proj, name="SemiRed", color=[1.0, 0.0, 0.0, 0.5])
        assert mat2["color"] == [1.0, 0.0, 0.0, 0.5]

    def test_assign_to_part(self):
        proj = _make_project()
        add_part(proj, "box", name="MyBox")
        create_material(proj, name="BlueMat", color=[0.0, 0.0, 1.0])

        result = assign_material(proj, material_index=0, part_index=0)
        assert result["material"] == "BlueMat"
        assert result["part"] == "MyBox"
        # Material should track the assignment
        assert 0 in proj["materials"][0]["assigned_to"]
        # Part should reference the material
        assert proj["parts"][0]["material_index"] == 0

    def test_set_property(self):
        proj = _make_project()
        create_material(proj, name="Editable")

        set_material_property(proj, 0, "roughness", 0.9)
        assert proj["materials"][0]["roughness"] == 0.9

        set_material_property(proj, 0, "name", "Renamed")
        assert proj["materials"][0]["name"] == "Renamed"

        set_material_property(proj, 0, "color", [0.1, 0.2, 0.3, 1.0])
        assert proj["materials"][0]["color"] == [0.1, 0.2, 0.3, 1.0]

    def test_set_invalid_property(self):
        proj = _make_project()
        create_material(proj)

        with pytest.raises(ValueError):
            set_material_property(proj, 0, "nonexistent_prop", 42)

        with pytest.raises(ValueError, match="maximum"):
            set_material_property(proj, 0, "metallic", 2.0)

    def test_list_presets(self):
        presets = list_presets()
        assert isinstance(presets, list)
        assert len(presets) == len(PRESETS)
        names = {p["name"] for p in presets}
        assert "steel" in names
        assert "gold" in names
        for p in presets:
            assert "name" in p
            assert "color" in p
            assert "metallic" in p
            assert "roughness" in p
