# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin4:
    def test_tower_defense_setup(self, tmp_path):
        """Realistic workflow: set up a tower defense game project."""
        from cli_anything.sbox.core import project as project_mod
        from cli_anything.sbox.core import scene as scene_mod
        from cli_anything.sbox.core import codegen as codegen_mod
        from cli_anything.sbox.core import input_config as input_config_mod
        from cli_anything.sbox.core import collision_config as collision_config_mod

        # Create project with custom settings
        proj = project_mod.create_project(
            name="TowerDefense",
            max_players=4,
            tick_rate=30,
            output_dir=str(tmp_path),
        )
        assert proj["max_players"] == 4
        assert proj["tick_rate"] == 30

        # Generate TowerData GameResource
        tower_data = codegen_mod.generate_gameresource(
            class_name="TowerData",
            display_name="Tower Data",
            extension="tower",
            properties=[
                {"name": "Damage", "type": "float", "default": "10f"},
                {"name": "Range", "type": "float", "default": "500f"},
                {"name": "FireRate", "type": "float", "default": "1.5f"},
                {"name": "Cost", "type": "int", "default": "100"},
            ],
        )
        tower_data_path = os.path.join(str(tmp_path), "Code", "TowerData.cs")
        os.makedirs(os.path.dirname(tower_data_path), exist_ok=True)
        with open(tower_data_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(tower_data["content"])

        # Generate Tower component (with properties: Damage, Range, FireRate)
        tower_comp = codegen_mod.generate_component(
            class_name="Tower",
            properties=[
                {"name": "Damage", "type": "float", "default": "10f"},
                {"name": "Range", "type": "float", "default": "500f"},
                {"name": "FireRate", "type": "float", "default": "1.5f"},
            ],
            lifecycle_methods=["OnUpdate"],
        )
        tower_comp_path = os.path.join(str(tmp_path), "Code", "Tower.cs")
        with open(tower_comp_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(tower_comp["content"])

        # Generate Enemy component (with Health, Speed, networked)
        enemy_comp = codegen_mod.generate_component(
            class_name="Enemy",
            properties=[
                {"name": "Health", "type": "float", "default": "100f"},
                {"name": "Speed", "type": "float", "default": "150f"},
            ],
            lifecycle_methods=["OnUpdate", "OnFixedUpdate"],
            is_networked=True,
        )
        enemy_comp_path = os.path.join(str(tmp_path), "Code", "Enemy.cs")
        with open(enemy_comp_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(enemy_comp["content"])

        # Add GameManager object to scene
        scene_path = os.path.join(str(tmp_path), "Assets", "scenes", "minimal.scene")
        gm_guid = scene_mod.add_object(scene_path, "GameManager")
        assert gm_guid

        # Add SpawnPoint objects
        sp1_guid = scene_mod.add_object(
            scene_path, "SpawnPoint_A", position="500,0,0",
        )
        sp2_guid = scene_mod.add_object(
            scene_path, "SpawnPoint_B", position="-500,0,0",
        )
        assert sp1_guid and sp2_guid

        # Configure custom input actions
        input_cfg = os.path.join(str(tmp_path), "ProjectSettings", "Input.config")
        for action_name, key in [
            ("PlaceTower", "mouse1"),
            ("SellTower", "Delete"),
            ("UpgradeTower", "U"),
        ]:
            input_config_mod.add_action(
                config_path=input_cfg,
                name=action_name,
                group="TowerDefense",
                keyboard_code=key,
            )

        # Verify custom actions exist
        actions = input_config_mod.list_actions(input_cfg)
        action_names = [a["Name"] for a in actions]
        assert "PlaceTower" in action_names
        assert "SellTower" in action_names
        assert "UpgradeTower" in action_names

        # Verify all files and configs
        assert os.path.isfile(tower_data_path)
        assert os.path.isfile(tower_comp_path)
        assert os.path.isfile(enemy_comp_path)
        assert os.path.isfile(scene_path)
        assert os.path.isfile(proj["sbproj"])

        # Verify scene has the added objects
        objects = scene_mod.list_objects(scene_path)
        obj_names = [o["name"] for o in objects]
        assert "GameManager" in obj_names
        assert "SpawnPoint_A" in obj_names
        assert "SpawnPoint_B" in obj_names

        # Verify enemy is networked (partial class)
        with open(enemy_comp_path, "r", encoding="utf-8") as f:
            enemy_content = f.read()
        assert "partial class Enemy" in enemy_content
        assert "[Sync]" in enemy_content

        # Print all artifact paths
        print(f"\n  Project:      {tmp_path}")
        print(f"  .sbproj:      {proj['sbproj']}")
        print(f"  Scene:        {scene_path}")
        print(f"  TowerData.cs: {tower_data_path}")
        print(f"  Tower.cs:     {tower_comp_path}")
        print(f"  Enemy.cs:     {enemy_comp_path}")
        print(f"  GameManager:  {gm_guid}")
        print(f"  SpawnPoint_A: {sp1_guid}")
        print(f"  SpawnPoint_B: {sp2_guid}")
        print(f"  Input actions: {action_names}")
