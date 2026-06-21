# ruff: noqa: F403, F405, E501
from .effects_base import *  # noqa: F403

# fmt: off
from .effects_p2 import EFFECT_REGISTRY  # noqa: E402,E501
from .effects_p3 import validate_params  # noqa: E402,E501
# fmt: on


def remove_effect(
    project: Dict[str, Any],
    effect_index: int,
    track_index: int = 0,
) -> Dict[str, Any]:
    """Remove an effect from a track by index."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    effects = tracks[track_index].get("effects", [])
    if effect_index < 0 or effect_index >= len(effects):
        raise IndexError(
            f"Effect index {effect_index} out of range (0-{len(effects) - 1})"
        )

    return effects.pop(effect_index)


def set_effect_param(
    project: Dict[str, Any],
    effect_index: int,
    param: str,
    value: Any,
    track_index: int = 0,
) -> None:
    """Set an effect parameter value."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    effects = tracks[track_index].get("effects", [])
    if effect_index < 0 or effect_index >= len(effects):
        raise IndexError(f"Effect index {effect_index} out of range")

    effect = effects[effect_index]
    name = effect["name"]
    spec = EFFECT_REGISTRY[name]["params"]

    if param not in spec:
        raise ValueError(
            f"Unknown parameter '{param}' for effect '{name}'. "
            f"Valid: {list(spec.keys())}"
        )

    # Validate
    test_params = dict(effect["params"])
    test_params[param] = value
    validated = validate_params(name, test_params)
    effect["params"] = validated


def list_effects(
    project: Dict[str, Any],
    track_index: int = 0,
) -> List[Dict[str, Any]]:
    """List effects on a track."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    effects = tracks[track_index].get("effects", [])
    result = []
    for i, e in enumerate(effects):
        result.append(
            {
                "index": i,
                "name": e["name"],
                "params": e["params"],
                "category": EFFECT_REGISTRY.get(e["name"], {}).get(
                    "category", "unknown"
                ),
            }
        )
    return result
