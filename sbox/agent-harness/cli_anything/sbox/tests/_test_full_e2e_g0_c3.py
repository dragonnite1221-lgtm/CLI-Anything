# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestE2EProjectWorkflowMixin3:
    def test_input_collision_workflow(self, tmp_path):
        """Create project, modify input and collision configs."""
        from cli_anything.sbox.core import project as project_mod
        from cli_anything.sbox.core import input_config as input_config_mod
        from cli_anything.sbox.core import collision_config as collision_config_mod

        # Create project
        project_mod.create_project(name="config_test", output_dir=str(tmp_path))
        input_cfg = os.path.join(str(tmp_path), "ProjectSettings", "Input.config")
        collision_cfg = os.path.join(str(tmp_path), "ProjectSettings", "Collision.config")

        # Add custom input action
        added_action = input_config_mod.add_action(
            config_path=input_cfg,
            name="PlaceTower",
            group="Gameplay",
            keyboard_code="mouse1",
        )
        assert added_action["Name"] == "PlaceTower"
        assert added_action["GroupName"] == "Gameplay"

        # Verify action appears in list
        actions = input_config_mod.list_actions(input_cfg)
        action_names = [a["Name"] for a in actions]
        assert "PlaceTower" in action_names

        # Standard actions should still be present
        assert "Forward" in action_names
        assert "Jump" in action_names

        # Add custom collision layer
        updated_defaults = collision_config_mod.add_layer(
            collision_cfg, "projectile", default="Collide",
        )
        assert "projectile" in updated_defaults

        # Add collision rule
        rule = collision_config_mod.add_rule(
            collision_cfg, "projectile", "solid", result="Collide",
        )
        assert rule["a"] == "projectile"
        assert rule["b"] == "solid"
        assert rule["r"] == "Collide"

        # Verify layers and rules
        layers_info = collision_config_mod.list_layers(collision_cfg)
        assert "projectile" in layers_info["defaults"]
        assert layers_info["defaults"]["solid"] == "Collide"
        # The new rule should appear in pairs
        pair_strs = [
            f"{p.get('a', p.get('A', ''))}-{p.get('b', p.get('B', ''))}"
            for p in layers_info["pairs"]
        ]
        assert "projectile-solid" in pair_strs

        print(f"\n  Input.config:     {input_cfg}")
        print(f"  Collision.config: {collision_cfg}")
        print(f"  Actions count:    {len(actions)}")
        print(f"  Layers:           {list(layers_info['defaults'].keys())}")
