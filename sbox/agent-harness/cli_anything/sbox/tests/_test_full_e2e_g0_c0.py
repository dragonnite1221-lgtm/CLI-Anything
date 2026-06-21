# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin0:
    """End-to-end tests creating real s&box projects and manipulating them."""
    def test_full_project_creation(self, tmp_path):
        """Create a project, verify all files exist, verify scene is valid JSON."""
        from cli_anything.sbox.core import project as project_mod

        result = project_mod.create_project(
            name="test_proj",
            output_dir=str(tmp_path),
        )

        # Verify returned info dict
        assert result["name"] == "test_proj"
        assert result["type"] == "game"
        assert result["max_players"] == 64
        assert result["tick_rate"] == 50

        # .sbproj exists and is valid JSON
        sbproj_path = result["sbproj"]
        assert os.path.isfile(sbproj_path)
        with open(sbproj_path, "r", encoding="utf-8") as f:
            sbproj_data = json.load(f)
        assert sbproj_data["Title"] == "test_proj"
        assert sbproj_data["Type"] == "game"

        # Assets/scenes/minimal.scene exists and is valid JSON
        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")
        assert os.path.isfile(scene_path)
        with open(scene_path, "r", encoding="utf-8") as f:
            scene_data = json.load(f)
        assert "GameObjects" in scene_data
        assert "SceneProperties" in scene_data
        assert len(scene_data["GameObjects"]) > 0

        # Code/Assembly.cs exists
        code_asm = os.path.join(str(tmp_path), "Code", "Assembly.cs")
        assert os.path.isfile(code_asm)

        # Editor/Assembly.cs exists
        editor_asm = os.path.join(str(tmp_path), "Editor", "Assembly.cs")
        assert os.path.isfile(editor_asm)

        # ProjectSettings configs exist
        input_cfg = os.path.join(str(tmp_path), "ProjectSettings", "Input.config")
        collision_cfg = os.path.join(str(tmp_path), "ProjectSettings", "Collision.config")
        assert os.path.isfile(input_cfg)
        assert os.path.isfile(collision_cfg)

        # Verify configs are valid JSON
        with open(input_cfg, "r", encoding="utf-8") as f:
            json.load(f)
        with open(collision_cfg, "r", encoding="utf-8") as f:
            json.load(f)

        # Print artifact paths
        print(f"\n  Project root: {tmp_path}")
        print(f"  .sbproj:      {sbproj_path}")
        print(f"  Scene:        {scene_path}")
        print(f"  Code asm:     {code_asm}")
        print(f"  Editor asm:   {editor_asm}")
        print(f"  Input.config: {input_cfg}")
        print(f"  Collision:    {collision_cfg}")
