# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p3 import FILTER_REGISTRY  # noqa: E402,E501
# fmt: on


def get_filter_info(name: str) -> Dict[str, Any]:
    """Get detailed info about a filter."""
    if name not in FILTER_REGISTRY:
        raise ValueError(
            f"Unknown filter: {name}. Use 'filter list-available' to see options."
        )
    info = FILTER_REGISTRY[name]
    return {
        "name": name,
        "category": info["category"],
        "description": info["description"],
        "params": info["params"],
        "engine": info["engine"],
    }


def validate_params(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fill defaults for filter parameters."""
    if name not in FILTER_REGISTRY:
        raise ValueError(f"Unknown filter: {name}")

    spec = FILTER_REGISTRY[name]["params"]
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
        raise ValueError(f"Unknown parameters for filter '{name}': {unknown}")

    return result


def add_filter(
    project: Dict[str, Any],
    name: str,
    layer_index: int = 0,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a filter to a layer."""
    layers = project.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(
            f"Layer index {layer_index} out of range (0-{len(layers) - 1})"
        )

    if name not in FILTER_REGISTRY:
        raise ValueError(f"Unknown filter: {name}")

    validated = validate_params(name, params or {})

    filter_entry = {
        "name": name,
        "params": validated,
    }

    layer = layers[layer_index]
    if "filters" not in layer:
        layer["filters"] = []
    layer["filters"].append(filter_entry)

    return filter_entry


def remove_filter(
    project: Dict[str, Any],
    filter_index: int,
    layer_index: int = 0,
) -> Dict[str, Any]:
    """Remove a filter from a layer by index."""
    layers = project.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(f"Layer index {layer_index} out of range")

    layer = layers[layer_index]
    filters = layer.get("filters", [])
    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(
            f"Filter index {filter_index} out of range (0-{len(filters) - 1})"
        )

    return filters.pop(filter_index)
