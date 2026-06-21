# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def add_layer(
    project: Dict[str, Any],
    name: str = "New Layer",
    layer_type: str = "image",
    source: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fill: str = "transparent",
    opacity: float = 1.0,
    blend_mode: str = "normal",
    position: Optional[int] = None,
    offset_x: int = 0,
    offset_y: int = 0,
) -> Dict[str, Any]:
    """Add a new layer to the project.

    Args:
        project: The project dict
        name: Layer name
        layer_type: "image", "text", "solid"
        source: Path to source image file (for image layers)
        width: Layer width (defaults to canvas width)
        height: Layer height (defaults to canvas height)
        fill: Fill type for new layers: "transparent", "white", "black", or hex color
        opacity: Layer opacity (0.0-1.0)
        blend_mode: Compositing blend mode
        position: Insert position (0=top, None=top)
        offset_x: Horizontal offset from canvas origin
        offset_y: Vertical offset from canvas origin

    Returns:
        The new layer dict
    """
    if blend_mode not in BLEND_MODES:
        raise ValueError(f"Invalid blend mode '{blend_mode}'. Valid: {BLEND_MODES}")
    if not 0.0 <= opacity <= 1.0:
        raise ValueError(f"Opacity must be 0.0-1.0, got {opacity}")
    if layer_type not in ("image", "text", "solid"):
        raise ValueError(f"Invalid layer type '{layer_type}'. Use: image, text, solid")
    if layer_type == "image" and source and not os.path.exists(source):
        raise FileNotFoundError(f"Source image not found: {source}")

    canvas = project["canvas"]
    layer_w = width or canvas["width"]
    layer_h = height or canvas["height"]

    # Generate next layer ID
    existing_ids = [l.get("id", 0) for l in project.get("layers", [])]
    next_id = max(existing_ids, default=-1) + 1

    layer = {
        "id": next_id,
        "name": name,
        "type": layer_type,
        "width": layer_w,
        "height": layer_h,
        "visible": True,
        "opacity": opacity,
        "blend_mode": blend_mode,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "filters": [],
    }

    if layer_type == "image":
        layer["source"] = source
        layer["fill"] = fill if not source else None
    elif layer_type == "solid":
        layer["fill"] = fill
    elif layer_type == "text":
        layer["text"] = ""
        layer["font"] = "Arial"
        layer["font_size"] = 24
        layer["color"] = "#000000"

    if "layers" not in project:
        project["layers"] = []

    if position is not None:
        position = max(0, min(position, len(project["layers"])))
        project["layers"].insert(position, layer)
    else:
        project["layers"].insert(0, layer)  # Top of stack

    return layer
