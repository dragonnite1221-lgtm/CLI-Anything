# ruff: noqa: F403, F405, E501
from .collision_config_base import *  # noqa: F403

# fmt: off
from .collision_config_p1 import load_collision_config, save_collision_config  # noqa: E402,E501
# fmt: on


def remove_rule(config_path: str, layer_a: str, layer_b: str) -> bool:
    """Remove a collision pair rule.

    Matches the pair in either order.

    Args:
        config_path: Absolute path to the Collision.config file.
        layer_a: First layer name.
        layer_b: Second layer name.

    Returns:
        True if a matching rule was found and removed, False otherwise.
    """
    data = load_collision_config(config_path)
    pairs = data.get("Pairs", [])
    original_len = len(pairs)

    data["Pairs"] = [
        p
        for p in pairs
        if not (
            (p["a"] == layer_a and p["b"] == layer_b)
            or (p["a"] == layer_b and p["b"] == layer_a)
        )
    ]

    if len(data["Pairs"]) < original_len:
        save_collision_config(config_path, data)
        return True

    return False


def get_default_collision_config() -> dict:
    """Return the default s&box Collision.config.

    Includes the standard layers (solid, world, trigger, ladder, water,
    playerclip) and the default pair rules.

    Returns:
        A complete Collision.config dict ready to be saved.
    """
    return {
        "Version": 2,
        "Defaults": {
            "solid": "Collide",
            "world": "Collide",
            "trigger": "Trigger",
            "ladder": "Ignore",
            "water": "Trigger",
        },
        "Pairs": [
            {"a": "solid", "b": "solid", "r": "Collide"},
            {"a": "trigger", "b": "playerclip", "r": "Ignore"},
            {"a": "trigger", "b": "solid", "r": "Trigger"},
            {"a": "playerclip", "b": "solid", "r": "Collide"},
        ],
        "__guid": str(uuid.uuid4()),
        "__schema": "configdata",
        "__type": "CollisionRules",
        "__version": 2,
    }
