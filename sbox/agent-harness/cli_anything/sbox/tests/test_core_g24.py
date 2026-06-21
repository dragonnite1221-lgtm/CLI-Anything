# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAssetRenameMove:
    """Tests for export.rename_asset and export.move_asset."""

    def _make_project_with_widget(self, tmp_path):
        """Build a project with a widget.vmdl + a scene + a prefab that reference it."""
        info = create_project("Refactor", output_dir=str(tmp_path / "Refactor"))
        proj_dir = os.path.dirname(info["sbproj"])

        # Asset on disk
        widget = os.path.join(proj_dir, "Assets", "models", "team", "widget.vmdl")
        os.makedirs(os.path.dirname(widget), exist_ok=True)
        with open(widget, "w", encoding="utf-8") as f:
            f.write("<MODEL>")

        # Scene referencing it
        scene_path = os.path.join(proj_dir, "Assets", "scenes", "level.scene")
        create_scene("level", output_path=scene_path, include_defaults=False)
        add_object(
            scene_path,
            "Box",
            components=[
                {"__type": "Sandbox.ModelRenderer", "Model": "models/team/widget.vmdl"},
            ],
        )

        # Prefab referencing the same model
        prefab_path = os.path.join(proj_dir, "Assets", "prefabs", "boxer.prefab")
        create_prefab(
            "boxer",
            output_path=prefab_path,
            components=[
                {"__type": "Sandbox.ModelRenderer", "Model": "models/team/widget.vmdl"},
            ],
        )

        return proj_dir, scene_path, prefab_path

    def test_rename_updates_scene_and_prefab(self, tmp_path):
        proj_dir, scene_path, prefab_path = self._make_project_with_widget(tmp_path)

        result = rename_asset(proj_dir, "models/team/widget.vmdl", "gizmo.vmdl")

        assert result["new_path"] == "models/team/gizmo.vmdl"
        assert result["file_renamed"] is True
        # Both the scene and prefab should appear in references_updated
        files = sorted(r["file"] for r in result["references_updated"])
        assert any("level.scene" in f for f in files)
        assert any("boxer.prefab" in f for f in files)

        # The new file exists, the old one doesn't
        assert os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "team", "gizmo.vmdl")
        )
        assert not os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "team", "widget.vmdl")
        )

        # Refs in the scene/prefab are rewritten
        s_refs = extract_asset_refs(scene_path)
        assert "models/team/gizmo.vmdl" in s_refs.get("models", [])
        p_refs = prefab_extract_asset_refs(prefab_path)
        assert "models/team/gizmo.vmdl" in p_refs.get("models", [])

    def test_rename_preserves_extension(self, tmp_path):
        proj_dir, _, _ = self._make_project_with_widget(tmp_path)
        # Pass new name without extension; existing .vmdl should be preserved
        result = rename_asset(proj_dir, "models/team/widget.vmdl", "gizmo")
        assert result["new_path"] == "models/team/gizmo.vmdl"

    def test_rename_dry_run(self, tmp_path):
        proj_dir, _, _ = self._make_project_with_widget(tmp_path)
        result = rename_asset(
            proj_dir, "models/team/widget.vmdl", "gizmo.vmdl", dry_run=True
        )
        assert result["dry_run"] is True
        assert result["file_renamed"] is False
        assert result["references_would_update"] == 2
        # File should still exist at original path
        assert os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "team", "widget.vmdl")
        )

    def test_rename_target_exists(self, tmp_path):
        proj_dir, _, _ = self._make_project_with_widget(tmp_path)
        # Pre-create the target
        existing = os.path.join(proj_dir, "Assets", "models", "team", "gizmo.vmdl")
        with open(existing, "w", encoding="utf-8") as f:
            f.write("<other>")

        with pytest.raises(FileExistsError):
            rename_asset(proj_dir, "models/team/widget.vmdl", "gizmo.vmdl")

    def test_rename_source_missing(self, tmp_path):
        proj_dir, _, _ = self._make_project_with_widget(tmp_path)
        with pytest.raises(FileNotFoundError):
            rename_asset(proj_dir, "models/nope/missing.vmdl", "x.vmdl")

    def test_move_to_new_directory(self, tmp_path):
        proj_dir, scene_path, _ = self._make_project_with_widget(tmp_path)

        result = move_asset(
            proj_dir, "models/team/widget.vmdl", "models/shared/widget.vmdl"
        )
        assert result["file_moved"] is True
        assert result["new_path"] == "models/shared/widget.vmdl"

        # File moved
        assert os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "shared", "widget.vmdl")
        )
        assert not os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "team", "widget.vmdl")
        )

        # Refs updated
        s_refs = extract_asset_refs(scene_path)
        assert "models/shared/widget.vmdl" in s_refs.get("models", [])

    def test_move_dry_run(self, tmp_path):
        proj_dir, _, _ = self._make_project_with_widget(tmp_path)
        result = move_asset(
            proj_dir,
            "models/team/widget.vmdl",
            "models/shared/widget.vmdl",
            dry_run=True,
        )
        assert result["dry_run"] is True
        assert result["file_moved"] is False
        assert result["references_would_update"] == 2
        assert os.path.isfile(
            os.path.join(proj_dir, "Assets", "models", "team", "widget.vmdl")
        )
