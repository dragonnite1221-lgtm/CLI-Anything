# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAssetRefGraph:
    """Tests for export.find_asset_refs and find_unused_assets."""

    def _make_project(self, tmp_path):
        """Build a minimal project with a scene + prefab + a stray unused model."""
        info = create_project("RefTest", output_dir=str(tmp_path / "RefTest"))
        proj_dir = os.path.dirname(info["sbproj"])

        # Custom scene with a known asset reference
        scene_path = os.path.join(proj_dir, "Assets", "scenes", "level.scene")
        os.makedirs(os.path.dirname(scene_path), exist_ok=True)
        create_scene("level", output_path=scene_path, include_defaults=False)
        add_object(
            scene_path,
            "Box",
            components=[
                {
                    "__type": "Sandbox.ModelRenderer",
                    "Model": "models/myteam/widget.vmdl",
                },
            ],
        )

        # Prefab that references the same model
        prefab_path = os.path.join(proj_dir, "Assets", "prefabs", "widget.prefab")
        os.makedirs(os.path.dirname(prefab_path), exist_ok=True)
        create_prefab(
            "widget",
            output_path=prefab_path,
            components=[
                {
                    "__type": "Sandbox.ModelRenderer",
                    "Model": "models/myteam/widget.vmdl",
                },
            ],
        )

        # Create the actual asset files (so list_assets sees them)
        widget_vmdl = os.path.join(
            proj_dir, "Assets", "models", "myteam", "widget.vmdl"
        )
        os.makedirs(os.path.dirname(widget_vmdl), exist_ok=True)
        with open(widget_vmdl, "w", encoding="utf-8") as f:
            f.write("<MODEL_PLACEHOLDER>")

        # Unused asset
        unused_vmdl = os.path.join(
            proj_dir, "Assets", "models", "myteam", "unused.vmdl"
        )
        with open(unused_vmdl, "w", encoding="utf-8") as f:
            f.write("<UNUSED_MODEL>")

        # Unused material
        unused_mat = os.path.join(proj_dir, "Assets", "materials", "unused.vmat")
        os.makedirs(os.path.dirname(unused_mat), exist_ok=True)
        with open(unused_mat, "w", encoding="utf-8") as f:
            f.write('Layer0 { shader "complex.shader" }')

        return proj_dir

    def test_find_asset_refs_finds_both(self, tmp_path):
        proj_dir = self._make_project(tmp_path)
        refs = find_asset_refs(proj_dir, "models/myteam/widget.vmdl")
        assert len(refs) == 2
        files = sorted(r["file"] for r in refs)
        assert any("level.scene" in f for f in files)
        assert any("widget.prefab" in f for f in files)
        for r in refs:
            assert r["category"] == "models"

    def test_find_asset_refs_case_insensitive(self, tmp_path):
        proj_dir = self._make_project(tmp_path)
        refs = find_asset_refs(proj_dir, "MODELS/MyTeam/Widget.VMDL")
        assert len(refs) == 2

    def test_find_asset_refs_none(self, tmp_path):
        proj_dir = self._make_project(tmp_path)
        refs = find_asset_refs(proj_dir, "models/nonexistent/foo.vmdl")
        assert refs == []

    def test_find_unused_assets(self, tmp_path):
        proj_dir = self._make_project(tmp_path)
        unused = find_unused_assets(proj_dir)
        unused_paths = sorted(u["path"].replace("\\", "/") for u in unused)
        # Both unused.vmdl and unused.vmat should be flagged
        assert any("unused.vmdl" in p for p in unused_paths)
        assert any("unused.vmat" in p for p in unused_paths)
        # widget.vmdl is referenced -> should NOT be flagged
        assert not any("widget.vmdl" in p for p in unused_paths)

    def test_find_unused_assets_filtered_by_type(self, tmp_path):
        proj_dir = self._make_project(tmp_path)
        unused = find_unused_assets(proj_dir, asset_types=["material"])
        types = {u["type"] for u in unused}
        # Only materials should appear
        assert types <= {"material"}
        assert any("unused.vmat" in u["path"].replace("\\", "/") for u in unused)
