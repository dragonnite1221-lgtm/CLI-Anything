# ruff: noqa: F403, F405, E501
from .modifiers_base import *  # noqa: F403

# fmt: off
from .modifiers_p2 import MODIFIER_REGISTRY  # noqa: E402,E501
from .modifiers_p3 import validate_params  # noqa: E402,E501
# fmt: on


def set_modifier_param(
    project: Dict[str, Any],
    modifier_index: int,
    param: str,
    value: Any,
    object_index: int = 0,
) -> None:
    """Set a modifier parameter value."""
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(f"Object index {object_index} out of range")

    obj = objects[object_index]
    modifiers = obj.get("modifiers", [])
    if modifier_index < 0 or modifier_index >= len(modifiers):
        raise IndexError(f"Modifier index {modifier_index} out of range")

    mod = modifiers[modifier_index]
    mod_type = mod["type"]
    spec = MODIFIER_REGISTRY[mod_type]["params"]

    if param not in spec:
        raise ValueError(
            f"Unknown parameter '{param}' for modifier '{mod_type}'. Valid: {list(spec.keys())}"
        )

    # Validate using the spec
    test_params = dict(mod["params"])
    test_params[param] = value
    validated = validate_params(mod_type, test_params)
    mod["params"] = validated


def list_modifiers(
    project: Dict[str, Any],
    object_index: int = 0,
) -> List[Dict[str, Any]]:
    """List modifiers on an object."""
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(f"Object index {object_index} out of range")

    obj = objects[object_index]
    result = []
    for i, mod in enumerate(obj.get("modifiers", [])):
        result.append(
            {
                "index": i,
                "type": mod["type"],
                "name": mod.get("name", mod["type"]),
                "bpy_type": mod.get("bpy_type", "UNKNOWN"),
                "params": mod["params"],
                "category": MODIFIER_REGISTRY.get(mod["type"], {}).get(
                    "category", "unknown"
                ),
            }
        )
    return result
