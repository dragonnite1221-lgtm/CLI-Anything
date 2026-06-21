# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestExport:
    """Tests for cli_anything.sbox.core.export."""

    def _create_project_with_assets(self, tmp_path):
        """Helper: create a project with known asset files and return root path."""
        info = create_project("AssetTest", output_dir=str(tmp_path / "AssetTest"))
        root = tmp_path / "AssetTest"

        # Add additional asset files
        # A prefab
        prefab_dir = root / "Assets" / "prefabs"
        prefab_dir.mkdir(parents=True, exist_ok=True)
        create_prefab("Turret", output_path=str(prefab_dir / "turret.prefab"))

        # A C# file
        code_dir = root / "Assets" / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        (code_dir / "PlayerHealth.cs").write_text(
            "public class PlayerHealth {}", encoding="utf-8"
        )

        return str(root)

    def test_list_assets(self, tmp_path):
        """List assets in a project directory."""
        project_dir = self._create_project_with_assets(tmp_path)

        assets = list_assets(project_dir)
        assert len(assets) >= 3  # minimal.scene + turret.prefab + PlayerHealth.cs

        types = {a["type"] for a in assets}
        assert "scene" in types
        assert "prefab" in types
        assert "code" in types

        # Each asset should have required keys
        for asset in assets:
            assert "path" in asset
            assert "type" in asset
            assert "name" in asset
            assert "size_bytes" in asset

    def test_list_assets_filtered(self, tmp_path):
        """Filter assets by type."""
        project_dir = self._create_project_with_assets(tmp_path)

        # Filter to scenes only
        scenes = list_assets(project_dir, asset_type="scene")
        for asset in scenes:
            assert asset["type"] == "scene"
            assert asset["name"].endswith(".scene")

        # Filter to prefabs only
        prefabs = list_assets(project_dir, asset_type="prefab")
        for asset in prefabs:
            assert asset["type"] == "prefab"
            assert asset["name"].endswith(".prefab")

        # Scenes and prefabs should not overlap
        scene_names = {a["name"] for a in scenes}
        prefab_names = {a["name"] for a in prefabs}
        assert scene_names.isdisjoint(prefab_names)

    def test_find_project_dir(self, tmp_path):
        """Find project dir from a subdirectory."""
        info = create_project("FindDir", output_dir=str(tmp_path / "FindDir"))
        root = tmp_path / "FindDir"

        # Create a nested directory
        nested = root / "Assets" / "scenes" / "subdir"
        nested.mkdir(parents=True, exist_ok=True)

        # find_project_dir should walk up and find the root
        found = find_project_dir(str(nested))
        assert found is not None
        # Normalize paths for comparison
        assert os.path.normcase(os.path.normpath(found)) == os.path.normcase(
            os.path.normpath(str(root))
        )

        # Should also work from a file inside the project
        scene_file = root / "Assets" / "scenes" / "minimal.scene"
        found_from_file = find_project_dir(str(scene_file))
        assert found_from_file is not None
        assert os.path.normcase(os.path.normpath(found_from_file)) == os.path.normcase(
            os.path.normpath(str(root))
        )
