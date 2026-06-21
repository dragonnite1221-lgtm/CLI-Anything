# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestInputConfig:
    """Tests for cli_anything.sbox.core.input_config."""

    def _write_default_config(self, tmp_path):
        """Helper: write default input config to a temp file and return path."""
        config_path = str(tmp_path / "Input.config")
        data = get_default_input_config()
        save_input_config(config_path, data)
        return config_path

    def test_get_default_config(self):
        """Default config has all standard actions."""
        config = get_default_input_config()
        actions = config["Actions"]
        names = [a["Name"] for a in actions]

        assert "Forward" in names
        assert "Backward" in names
        assert "Jump" in names
        assert "Attack1" in names
        assert "Reload" in names
        assert "Use" in names

        # Should have __guid and __type metadata
        assert "__guid" in config
        assert config["__type"] == "InputSettings"

    def test_add_action(self, tmp_path):
        """Add a new action and verify it appears."""
        config_path = self._write_default_config(tmp_path)

        new_action = add_action(
            config_path,
            name="Sprint",
            group="Movement",
            keyboard_code="shift",
        )
        assert new_action["Name"] == "Sprint"
        assert new_action["GroupName"] == "Movement"
        assert new_action["KeyboardCode"] == "shift"

        # Verify persistence
        actions = list_actions(config_path)
        names = [a["Name"] for a in actions]
        assert "Sprint" in names

    def test_add_duplicate_action(self, tmp_path):
        """Adding duplicate action should raise ValueError."""
        config_path = self._write_default_config(tmp_path)

        with pytest.raises(ValueError, match="already exists"):
            add_action(config_path, name="Forward", group="Movement")

    def test_remove_action(self, tmp_path):
        """Remove an action and verify it's gone."""
        config_path = self._write_default_config(tmp_path)

        removed = remove_action(config_path, "Voice")
        assert removed is True

        actions = list_actions(config_path)
        names = [a["Name"] for a in actions]
        assert "Voice" not in names

    def test_set_action(self, tmp_path):
        """Modify action bindings."""
        config_path = self._write_default_config(tmp_path)

        updated = set_action(
            config_path,
            name="Jump",
            keyboard_code="F",
            group="Custom",
        )
        assert updated["KeyboardCode"] == "F"
        assert updated["GroupName"] == "Custom"

        # Verify persistence
        actions = list_actions(config_path)
        jump = [a for a in actions if a["Name"] == "Jump"][0]
        assert jump["KeyboardCode"] == "F"
        assert jump["GroupName"] == "Custom"

    def test_list_actions(self, tmp_path):
        """List all actions returns proper format."""
        config_path = self._write_default_config(tmp_path)

        actions = list_actions(config_path)
        assert isinstance(actions, list)
        assert len(actions) > 0

        for action in actions:
            assert "Name" in action
            assert isinstance(action["Name"], str)
