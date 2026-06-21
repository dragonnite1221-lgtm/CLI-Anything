# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCollisionConfig:
    """Tests for cli_anything.sbox.core.collision_config."""

    def _write_default_config(self, tmp_path):
        """Helper: write default collision config to a temp file and return path."""
        config_path = str(tmp_path / "Collision.config")
        data = get_default_collision_config()
        save_collision_config(config_path, data)
        return config_path

    def test_get_default_config(self):
        """Default config has standard layers."""
        config = get_default_collision_config()
        defaults = config["Defaults"]

        assert "solid" in defaults
        assert "world" in defaults
        assert "trigger" in defaults
        assert "ladder" in defaults
        assert "water" in defaults

        # Should have pairs
        pairs = config["Pairs"]
        assert isinstance(pairs, list)
        assert len(pairs) > 0

    def test_add_layer(self, tmp_path):
        """Add a custom collision layer."""
        config_path = self._write_default_config(tmp_path)

        updated_defaults = add_layer(config_path, "projectile", default="Collide")
        assert "projectile" in updated_defaults
        assert updated_defaults["projectile"] == "Collide"

        # Verify persistence
        data = load_collision_config(config_path)
        assert "projectile" in data["Defaults"]

    def test_remove_builtin_layer(self, tmp_path):
        """Removing built-in layer should raise ValueError."""
        config_path = self._write_default_config(tmp_path)

        with pytest.raises(ValueError, match="Cannot remove built-in layer"):
            remove_layer(config_path, "solid")

        with pytest.raises(ValueError, match="Cannot remove built-in layer"):
            remove_layer(config_path, "trigger")

    def test_add_rule(self, tmp_path):
        """Add a collision pair rule."""
        config_path = self._write_default_config(tmp_path)

        # First add custom layers so the rule makes sense
        add_layer(config_path, "projectile", default="Collide")
        add_layer(config_path, "enemy", default="Collide")

        rule = add_rule(config_path, "projectile", "enemy", result="Collide")
        assert rule["a"] == "projectile"
        assert rule["b"] == "enemy"
        assert rule["r"] == "Collide"

        # Verify persistence
        data = load_collision_config(config_path)
        pairs = data["Pairs"]
        matching = [
            p
            for p in pairs
            if (p["a"] == "projectile" and p["b"] == "enemy")
            or (p["a"] == "enemy" and p["b"] == "projectile")
        ]
        assert len(matching) == 1

    def test_remove_rule(self, tmp_path):
        """Remove a pair rule."""
        config_path = self._write_default_config(tmp_path)

        # Add a custom rule then remove it
        add_layer(config_path, "projectile", default="Collide")
        add_rule(config_path, "projectile", "solid", result="Collide")

        removed = remove_rule(config_path, "projectile", "solid")
        assert removed is True

        # Verify it's gone
        data = load_collision_config(config_path)
        pairs = data["Pairs"]
        matching = [
            p
            for p in pairs
            if (p["a"] == "projectile" and p["b"] == "solid")
            or (p["a"] == "solid" and p["b"] == "projectile")
        ]
        assert len(matching) == 0
