# ruff: noqa: F403, F405, E501
from .effects_base import *  # noqa: F403

# fmt: off
from .effects_p2 import EFFECT_REGISTRY  # noqa: E402,E501
# fmt: on


def get_effect_info(name: str) -> Dict[str, Any]:
    """Get detailed info about an effect."""
    if name not in EFFECT_REGISTRY:
        raise ValueError(
            f"Unknown effect: {name}. Use 'effect list-available' to see options."
        )
    info = EFFECT_REGISTRY[name]
    return {
        "name": name,
        "category": info["category"],
        "description": info["description"],
        "params": info["params"],
    }


def validate_params(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fill defaults for effect parameters."""
    if name not in EFFECT_REGISTRY:
        raise ValueError(f"Unknown effect: {name}")

    spec = EFFECT_REGISTRY[name]["params"]
    result = {}

    for pname, pspec in spec.items():
        if pname in params:
            val = params[pname]
            ptype = pspec["type"]
            if ptype == "float":
                val = float(val)
                if "min" in pspec and val < pspec["min"]:
                    raise ValueError(
                        f"Parameter '{pname}' minimum is {pspec['min']}, got {val}"
                    )
                if "max" in pspec and val > pspec["max"]:
                    raise ValueError(
                        f"Parameter '{pname}' maximum is {pspec['max']}, got {val}"
                    )
            elif ptype == "int":
                val = int(val)
                if "min" in pspec and val < pspec["min"]:
                    raise ValueError(
                        f"Parameter '{pname}' minimum is {pspec['min']}, got {val}"
                    )
                if "max" in pspec and val > pspec["max"]:
                    raise ValueError(
                        f"Parameter '{pname}' maximum is {pspec['max']}, got {val}"
                    )
            elif ptype == "bool":
                val = str(val).lower() in ("true", "1", "yes")
            elif ptype == "str":
                val = str(val)
            result[pname] = val
        else:
            result[pname] = pspec.get("default")

    # Check for unknown params
    unknown = set(params.keys()) - set(spec.keys())
    if unknown:
        raise ValueError(f"Unknown parameters for effect '{name}': {unknown}")

    return result


def add_effect(
    project: Dict[str, Any],
    name: str,
    track_index: int = 0,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add an effect to a track."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(
            f"Track index {track_index} out of range (0-{len(tracks) - 1})"
        )

    if name not in EFFECT_REGISTRY:
        raise ValueError(f"Unknown effect: {name}")

    validated = validate_params(name, params or {})

    effect_entry = {
        "name": name,
        "params": validated,
    }

    track = tracks[track_index]
    track.setdefault("effects", []).append(effect_entry)
    return effect_entry
