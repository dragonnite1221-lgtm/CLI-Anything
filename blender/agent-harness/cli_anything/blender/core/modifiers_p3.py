# ruff: noqa: F403, F405, E501
from .modifiers_base import *  # noqa: F403

# fmt: off
from .modifiers_p2 import MODIFIER_REGISTRY  # noqa: E402,E501
# fmt: on


def validate_params(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fill defaults for modifier parameters."""
    if name not in MODIFIER_REGISTRY:
        raise ValueError(f"Unknown modifier: {name}")

    spec = MODIFIER_REGISTRY[name]["params"]
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

    # Warn about unknown params
    unknown = set(params.keys()) - set(spec.keys())
    if unknown:
        raise ValueError(f"Unknown parameters for modifier '{name}': {unknown}")

    return result


def add_modifier(
    project: Dict[str, Any],
    modifier_type: str,
    object_index: int = 0,
    name: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a modifier to an object.

    Args:
        project: The scene dict
        modifier_type: Modifier type name (e.g., "subdivision_surface")
        object_index: Index of the target object
        name: Custom modifier name (auto-generated if None)
        params: Override modifier parameters

    Returns:
        The new modifier entry dict
    """
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    if modifier_type not in MODIFIER_REGISTRY:
        raise ValueError(f"Unknown modifier: {modifier_type}")

    validated = validate_params(modifier_type, params or {})

    modifier_name = name or modifier_type.replace("_", " ").title()

    modifier_entry = {
        "type": modifier_type,
        "name": modifier_name,
        "bpy_type": MODIFIER_REGISTRY[modifier_type]["bpy_type"],
        "params": validated,
    }

    obj = objects[object_index]
    if "modifiers" not in obj:
        obj["modifiers"] = []
    obj["modifiers"].append(modifier_entry)

    return modifier_entry


def remove_modifier(
    project: Dict[str, Any],
    modifier_index: int,
    object_index: int = 0,
) -> Dict[str, Any]:
    """Remove a modifier from an object by index."""
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(f"Object index {object_index} out of range")

    obj = objects[object_index]
    modifiers = obj.get("modifiers", [])
    if modifier_index < 0 or modifier_index >= len(modifiers):
        raise IndexError(
            f"Modifier index {modifier_index} out of range (0-{len(modifiers) - 1})"
        )

    return modifiers.pop(modifier_index)
