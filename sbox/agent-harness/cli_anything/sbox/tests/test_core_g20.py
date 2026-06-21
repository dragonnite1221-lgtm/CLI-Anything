# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestProjectValidate:
    """Tests for validate.validate_project."""

    def test_validate_clean_project(self, tmp_path):
        info = create_project("Clean", output_dir=str(tmp_path / "Clean"))
        proj_dir = os.path.dirname(info["sbproj"])
        # The default scene only references engine built-ins - should be clean
        result = validate_project(proj_dir)
        assert result["broken_refs"] == []
        assert result["duplicate_guids"] == []

    def test_validate_detects_broken_refs(self, tmp_path):
        info = create_project("Broken", output_dir=str(tmp_path / "Broken"))
        proj_dir = os.path.dirname(info["sbproj"])

        scene_path = os.path.join(proj_dir, "Assets", "scenes", "broken.scene")
        create_scene("broken", output_path=scene_path, include_defaults=False)
        add_object(
            scene_path,
            "Bad",
            components=[
                {
                    "__type": "Sandbox.ModelRenderer",
                    "Model": "models/missing/whoops.vmdl",
                },
            ],
        )

        result = validate_project(proj_dir, check_inputs=False)
        broken_refs = [b["ref"] for b in result["broken_refs"]]
        assert any("missing/whoops" in r for r in broken_refs)
        assert result["ok"] is False
        assert result["issue_count"] >= 1

    def test_validate_detects_duplicate_guids(self, tmp_path):
        info = create_project("Dups", output_dir=str(tmp_path / "Dups"))
        proj_dir = os.path.dirname(info["sbproj"])

        scene_path = os.path.join(proj_dir, "Assets", "scenes", "dup.scene")
        create_scene("dup", output_path=scene_path, include_defaults=False)
        # Forcefully inject a duplicate GUID
        data = load_scene(scene_path)
        same_guid = "11111111-1111-1111-1111-111111111111"
        data["GameObjects"] = [
            {"__guid": same_guid, "Name": "A", "Components": [], "Children": []},
            {"__guid": same_guid, "Name": "B", "Components": [], "Children": []},
        ]
        save_scene(scene_path, data)

        result = validate_project(proj_dir, check_refs=False, check_inputs=False)
        assert any(g["guid"] == same_guid for g in result["duplicate_guids"])

    def test_validate_can_disable_checks(self, tmp_path):
        info = create_project("Disabled", output_dir=str(tmp_path / "Disabled"))
        proj_dir = os.path.dirname(info["sbproj"])
        result = validate_project(
            proj_dir, check_refs=False, check_guids=False, check_inputs=False
        )
        assert result["broken_refs"] == []
        assert result["duplicate_guids"] == []
        assert result["invalid_inputs"] == []
