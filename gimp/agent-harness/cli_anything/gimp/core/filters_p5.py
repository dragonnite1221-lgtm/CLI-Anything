# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p3 import FILTER_REGISTRY  # noqa: E402,E501
from .filters_p4 import validate_params  # noqa: E402,E501
# fmt: on


def set_filter_param(
    project: Dict[str, Any],
    filter_index: int,
    param: str,
    value: Any,
    layer_index: int = 0,
) -> None:
    """Set a filter parameter value."""
    layers = project.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(f"Layer index {layer_index} out of range")

    layer = layers[layer_index]
    filters = layer.get("filters", [])
    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(f"Filter index {filter_index} out of range")

    filt = filters[filter_index]
    name = filt["name"]
    spec = FILTER_REGISTRY[name]["params"]

    if param not in spec:
        raise ValueError(
            f"Unknown parameter '{param}' for filter '{name}'. Valid: {list(spec.keys())}"
        )

    # Validate using the spec
    test_params = dict(filt["params"])
    test_params[param] = value
    validated = validate_params(name, test_params)
    filt["params"] = validated


def list_filters(
    project: Dict[str, Any],
    layer_index: int = 0,
) -> List[Dict[str, Any]]:
    """List filters on a layer."""
    layers = project.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(f"Layer index {layer_index} out of range")

    layer = layers[layer_index]
    result = []
    for i, f in enumerate(layer.get("filters", [])):
        result.append(
            {
                "index": i,
                "name": f["name"],
                "params": f["params"],
                "category": FILTER_REGISTRY.get(f["name"], {}).get(
                    "category", "unknown"
                ),
            }
        )
    return result
