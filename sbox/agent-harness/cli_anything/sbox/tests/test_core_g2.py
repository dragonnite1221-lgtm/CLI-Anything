# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPrefab:
    """Tests for cli_anything.sbox.core.prefab."""

    def test_create_prefab(self, tmp_path):
        """Create a prefab and verify structure."""
        prefab_path = str(tmp_path / "test.prefab")
        data = create_prefab("TestPrefab", output_path=prefab_path)

        assert "RootObject" in data
        root = data["RootObject"]
        assert root["Name"] == "TestPrefab"
        assert "__guid" in root
        assert root["Enabled"] is True
        assert "Components" in root
        assert "Children" in root
        assert data["ResourceVersion"] == 1
        assert data["__version"] == 1

        # Verify file was written
        with open(prefab_path, "r", encoding="utf-8") as f:
            on_disk = json.load(f)
        assert on_disk["RootObject"]["Name"] == "TestPrefab"

    def test_create_prefab_with_components(self, tmp_path):
        """Create prefab with component presets."""
        prefab_path = str(tmp_path / "comps.prefab")
        data = create_prefab(
            "PhysicsPrefab",
            output_path=prefab_path,
            components=["model", "box_collider", "rigidbody"],
        )

        root = data["RootObject"]
        comp_types = [c["__type"] for c in root["Components"]]
        assert "Sandbox.ModelRenderer" in comp_types
        assert "Sandbox.BoxCollider" in comp_types
        assert "Sandbox.Rigidbody" in comp_types

        # Each component should have a unique __guid
        comp_guids = [c["__guid"] for c in root["Components"]]
        assert len(comp_guids) == len(set(comp_guids))

    def test_get_prefab_info(self, tmp_path):
        """Verify prefab info."""
        prefab_path = str(tmp_path / "info.prefab")
        create_prefab(
            "InfoPrefab",
            output_path=prefab_path,
            components=["model", "rigidbody"],
        )

        info = get_prefab_info(prefab_path)
        assert info["name"] == "InfoPrefab"
        assert "guid" in info
        assert info["path"] == prefab_path
        assert info["component_count"] == 2
        assert "Sandbox.ModelRenderer" in info["component_types"]
        assert "Sandbox.Rigidbody" in info["component_types"]
        assert info["children_count"] == 0
        assert info["network_mode"] == 0

    def test_from_scene_object(self, tmp_path):
        """Extract a scene object into a prefab."""
        scene_path = str(tmp_path / "source.scene")
        create_scene("source", output_path=scene_path)
        obj_guid = add_object(
            scene_path,
            "ExtractMe",
            position="10,20,30",
            components=["model", "rigidbody"],
        )

        prefab_path = str(tmp_path / "extracted.prefab")
        data = from_scene_object(scene_path, obj_guid, prefab_path)

        assert "RootObject" in data
        root = data["RootObject"]
        assert root["Name"] == "ExtractMe"
        assert root["Position"] == "10,20,30"

        comp_types = [c["__type"] for c in root.get("Components", [])]
        assert "Sandbox.ModelRenderer" in comp_types
        assert "Sandbox.Rigidbody" in comp_types

        # Verify the prefab file exists on disk
        assert os.path.isfile(prefab_path)
