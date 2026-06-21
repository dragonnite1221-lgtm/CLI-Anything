# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def set_layer_property(
    project: Dict[str, Any], index: int, prop: str, value: Any
) -> None:
    """Set a layer property."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range")

    layer = layers[index]

    if prop == "opacity":
        value = float(value)
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Opacity must be 0.0-1.0, got {value}")
        layer["opacity"] = value
    elif prop == "visible":
        layer["visible"] = str(value).lower() in ("true", "1", "yes")
    elif prop == "blend_mode" or prop == "mode":
        if value not in BLEND_MODES:
            raise ValueError(f"Invalid blend mode '{value}'. Valid: {BLEND_MODES}")
        layer["blend_mode"] = value
    elif prop == "name":
        layer["name"] = str(value)
    elif prop == "offset_x":
        layer["offset_x"] = int(value)
    elif prop == "offset_y":
        layer["offset_y"] = int(value)
    else:
        raise ValueError(
            f"Unknown property: {prop}. Valid: name, opacity, visible, mode, offset_x, offset_y"
        )


def get_layer(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get a layer by index."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")
    return layers[index]


def list_layers(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all layers with summary info."""
    result = []
    for i, l in enumerate(project.get("layers", [])):
        result.append(
            {
                "index": i,
                "id": l.get("id", i),
                "name": l.get("name", f"Layer {i}"),
                "type": l.get("type", "image"),
                "visible": l.get("visible", True),
                "opacity": l.get("opacity", 1.0),
                "blend_mode": l.get("blend_mode", "normal"),
                "size": f"{l.get('width', '?')}x{l.get('height', '?')}",
                "offset": f"({l.get('offset_x', 0)}, {l.get('offset_y', 0)})",
                "filter_count": len(l.get("filters", [])),
            }
        )
    return result


def flatten_layers(project: Dict[str, Any]) -> None:
    """Mark project for flattening (merge all visible layers into one)."""
    visible = [l for l in project.get("layers", []) if l.get("visible", True)]
    if not visible:
        raise ValueError("No visible layers to flatten")
    # Create a single flattened layer marker
    project["_flatten_pending"] = True


def merge_down(project: Dict[str, Any], index: int) -> None:
    """Mark layers for merging (layer at index merges into the one below)."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range")
    if index >= len(layers) - 1:
        raise ValueError("Cannot merge down the bottom layer")
    project["_merge_down_pending"] = index
