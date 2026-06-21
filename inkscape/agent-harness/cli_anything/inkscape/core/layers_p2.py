# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def set_layer_property(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> Dict[str, Any]:
    """Set a property on a layer."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")

    layer = layers[index]

    valid_props = {"name", "visible", "locked", "opacity"}
    if prop not in valid_props:
        raise ValueError(
            f"Unknown layer property: {prop}. Valid: {', '.join(sorted(valid_props))}"
        )

    if prop == "visible":
        if isinstance(value, str):
            value = value.lower() in ("true", "1", "yes")
        layer["visible"] = bool(value)
    elif prop == "locked":
        if isinstance(value, str):
            value = value.lower() in ("true", "1", "yes")
        layer["locked"] = bool(value)
    elif prop == "opacity":
        value = float(value)
        if value < 0 or value > 1:
            raise ValueError(f"Opacity must be 0.0-1.0: {value}")
        layer["opacity"] = value
    elif prop == "name":
        layer["name"] = str(value)

    return layer


def list_layers(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all layers in the document."""
    result = []
    for i, layer in enumerate(project.get("layers", [])):
        result.append(
            {
                "index": i,
                "id": layer.get("id", ""),
                "name": layer.get("name", ""),
                "visible": layer.get("visible", True),
                "locked": layer.get("locked", False),
                "opacity": layer.get("opacity", 1.0),
                "object_count": len(layer.get("objects", [])),
            }
        )
    return result


def reorder_layers(
    project: Dict[str, Any], from_index: int, to_index: int
) -> Dict[str, Any]:
    """Move a layer from one position to another in the stack."""
    layers = project.get("layers", [])
    if from_index < 0 or from_index >= len(layers):
        raise IndexError(f"From index {from_index} out of range (0-{len(layers) - 1})")
    if to_index < 0 or to_index >= len(layers):
        raise IndexError(f"To index {to_index} out of range (0-{len(layers) - 1})")

    layer = layers.pop(from_index)
    layers.insert(to_index, layer)

    return {
        "layer": layer.get("name", layer.get("id", "")),
        "from": from_index,
        "to": to_index,
    }


def get_layer(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get detailed info about a layer."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")

    layer = layers[index]

    # Get objects in this layer
    layer_obj_ids = set(layer.get("objects", []))
    layer_objects = []
    for i, obj in enumerate(project.get("objects", [])):
        if obj.get("id") in layer_obj_ids:
            layer_objects.append(
                {
                    "index": i,
                    "id": obj.get("id", ""),
                    "name": obj.get("name", ""),
                    "type": obj.get("type", "unknown"),
                }
            )

    return {
        "id": layer.get("id", ""),
        "name": layer.get("name", ""),
        "visible": layer.get("visible", True),
        "locked": layer.get("locked", False),
        "opacity": layer.get("opacity", 1.0),
        "objects": layer_objects,
    }
