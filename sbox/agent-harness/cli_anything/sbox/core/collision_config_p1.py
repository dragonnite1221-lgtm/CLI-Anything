# ruff: noqa: F403, F405, E501
from .collision_config_base import *  # noqa: F403


def load_collision_config(config_path: str) -> dict:
    """Load Collision.config JSON from disk.

    Args:
        config_path: Absolute path to the Collision.config file.

    Returns:
        Parsed JSON dict.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_collision_config(config_path: str, data: dict) -> None:
    """Save Collision.config JSON to disk.

    Args:
        config_path: Absolute path to the Collision.config file.
        data: The full config dict to write.
    """
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def list_layers(config_path: str) -> dict:
    """Return dict of layers and their defaults, plus pair rules.

    Args:
        config_path: Absolute path to the Collision.config file.

    Returns:
        Dict with "defaults" (layer name -> default behavior) and
        "pairs" (list of pair rule dicts with a, b, r keys).
    """
    data = load_collision_config(config_path)
    return {
        "defaults": data.get("Defaults", {}),
        "pairs": data.get("Pairs", []),
    }


def add_layer(
    config_path: str,
    name: str,
    default: str = "Collide",
) -> dict:
    """Add a new collision layer with its default behavior.

    Args:
        config_path: Absolute path to the Collision.config file.
        name: Layer name, e.g. "projectile".
        default: Default collision behavior - "Collide", "Trigger", or "Ignore".

    Returns:
        The updated defaults dict.

    Raises:
        ValueError: If default is not a valid result or layer already exists.
    """
    if default not in VALID_RESULTS:
        raise ValueError(
            f"Invalid default '{default}'. Must be one of: {', '.join(sorted(VALID_RESULTS))}"
        )

    data = load_collision_config(config_path)
    defaults = data.get("Defaults", {})

    if name in defaults:
        raise ValueError(f"Layer '{name}' already exists")

    defaults[name] = default
    data["Defaults"] = defaults
    save_collision_config(config_path, data)
    return defaults


def remove_layer(config_path: str, name: str) -> bool:
    """Remove a collision layer and all its pair rules.

    Cannot remove built-in layers: solid, trigger, ladder, water.

    Args:
        config_path: Absolute path to the Collision.config file.
        name: Layer name to remove.

    Returns:
        True if the layer was found and removed, False if it did not exist.

    Raises:
        ValueError: If attempting to remove a built-in layer.
    """
    if name in BUILTIN_LAYERS:
        raise ValueError(f"Cannot remove built-in layer '{name}'")

    data = load_collision_config(config_path)
    defaults = data.get("Defaults", {})

    if name not in defaults:
        return False

    del defaults[name]
    data["Defaults"] = defaults

    # Remove any pair rules referencing this layer
    pairs = data.get("Pairs", [])
    data["Pairs"] = [p for p in pairs if p["a"] != name and p["b"] != name]

    save_collision_config(config_path, data)
    return True


def add_rule(
    config_path: str,
    layer_a: str,
    layer_b: str,
    result: str = "Collide",
) -> dict:
    """Add or update a collision pair rule.

    If a rule for the given pair already exists (in either order), it is updated.

    Args:
        config_path: Absolute path to the Collision.config file.
        layer_a: First layer name.
        layer_b: Second layer name.
        result: Collision result - "Collide", "Trigger", or "Ignore".

    Returns:
        The pair rule dict that was added or updated.

    Raises:
        ValueError: If result is not valid.
    """
    if result not in VALID_RESULTS:
        raise ValueError(
            f"Invalid result '{result}'. Must be one of: {', '.join(sorted(VALID_RESULTS))}"
        )

    data = load_collision_config(config_path)
    pairs = data.get("Pairs", [])

    # Check for existing rule in either order
    for pair in pairs:
        if (pair["a"] == layer_a and pair["b"] == layer_b) or (
            pair["a"] == layer_b and pair["b"] == layer_a
        ):
            pair["r"] = result
            data["Pairs"] = pairs
            save_collision_config(config_path, data)
            return pair

    # Create new rule
    new_rule = {"a": layer_a, "b": layer_b, "r": result}
    pairs.append(new_rule)
    data["Pairs"] = pairs
    save_collision_config(config_path, data)
    return new_rule
