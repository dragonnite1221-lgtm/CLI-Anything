# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPrefabRefs:
    """Tests for prefab.extract_asset_refs."""

    def test_refs_from_prefab(self, tmp_path):
        prefab_path = str(tmp_path / "p.prefab")
        create_prefab(
            "p",
            output_path=prefab_path,
            components=["model", "rigidbody", "model_collider"],
        )
        refs = prefab_extract_asset_refs(prefab_path)
        assert "models" in refs
        assert "models/dev/box.vmdl" in refs["models"]


class TestPrefabModifyComponent:
    """Tests for prefab.modify_component."""

    def test_modify_by_type(self, tmp_path):
        prefab_path = str(tmp_path / "rb.prefab")
        create_prefab("rb", output_path=prefab_path, components=["model", "rigidbody"])
        result = prefab_modify_component(
            prefab_path,
            component_type="Sandbox.Rigidbody",
            properties={"Gravity": False, "MassOverride": 100},
        )
        assert result["component_type"] == "Sandbox.Rigidbody"
        assert "Gravity" in result["updated_keys"]
        assert "MassOverride" in result["updated_keys"]

        data = load_prefab(prefab_path)
        rb = next(
            c
            for c in data["RootObject"]["Components"]
            if c["__type"] == "Sandbox.Rigidbody"
        )
        assert rb["Gravity"] is False
        assert rb["MassOverride"] == 100

    def test_modify_by_guid(self, tmp_path):
        prefab_path = str(tmp_path / "guid.prefab")
        create_prefab("guid", output_path=prefab_path, components=["model"])
        data = load_prefab(prefab_path)
        comp_guid = data["RootObject"]["Components"][0]["__guid"]

        result = prefab_modify_component(
            prefab_path,
            component_guid=comp_guid,
            properties={"Tint": "1,0,0,1"},
        )
        assert result["component_guid"] == comp_guid

        data2 = load_prefab(prefab_path)
        assert data2["RootObject"]["Components"][0]["Tint"] == "1,0,0,1"

    def test_modify_not_found(self, tmp_path):
        prefab_path = str(tmp_path / "nf.prefab")
        create_prefab("nf", output_path=prefab_path, components=["model"])
        with pytest.raises(ValueError, match="not found"):
            prefab_modify_component(
                prefab_path, component_type="Sandbox.Missing", properties={"x": 1}
            )

    def test_modify_requires_identifier(self, tmp_path):
        prefab_path = str(tmp_path / "id.prefab")
        create_prefab("id", output_path=prefab_path, components=["model"])
        with pytest.raises(ValueError, match="component_guid or component_type"):
            prefab_modify_component(prefab_path, properties={"x": 1})

    def test_modify_requires_properties(self, tmp_path):
        prefab_path = str(tmp_path / "noprops.prefab")
        create_prefab("noprops", output_path=prefab_path, components=["model"])
        with pytest.raises(ValueError, match="No properties"):
            prefab_modify_component(prefab_path, component_type="Sandbox.ModelRenderer")
