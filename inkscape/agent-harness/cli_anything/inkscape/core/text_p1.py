# ruff: noqa: F403, F405, E501
from .text_base import *  # noqa: F403


def _default_layer_id(project: Dict[str, Any]) -> str:
    """Get the ID of the first layer."""
    layers = project.get("layers", [])
    if layers:
        return layers[0].get("id", "layer1")
    return ""


def _add_object(project: Dict[str, Any], obj: Dict[str, Any]) -> None:
    """Add an object to the project's objects list and its layer."""
    project.setdefault("objects", []).append(obj)

    layer_id = obj.get("layer", "")
    if layer_id:
        for layer in project.get("layers", []):
            if layer.get("id") == layer_id:
                layer.setdefault("objects", []).append(obj["id"])
                break


def add_text(
    project: Dict[str, Any],
    text: str = "Text",
    x: float = 0,
    y: float = 50,
    font_family: str = "sans-serif",
    font_size: float = 24,
    font_weight: str = "normal",
    font_style: str = "normal",
    fill: str = "#000000",
    text_anchor: str = "start",
    box_width: Optional[float] = None,
    box_height: Optional[float] = None,
    line_height: float = 1.2,
    name: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a text element to the document."""
    if not text:
        raise ValueError("Text content cannot be empty")
    if font_size <= 0:
        raise ValueError(f"Font size must be positive: {font_size}")
    if box_width is not None and box_width <= 0:
        raise ValueError(f"Text box width must be positive: {box_width}")
    if box_height is not None and box_height <= 0:
        raise ValueError(f"Text box height must be positive: {box_height}")
    if line_height <= 0:
        raise ValueError(f"Line height must be positive: {line_height}")

    # Build style string
    style_parts = {
        "font-family": font_family,
        "font-size": f"{font_size}px",
        "font-weight": font_weight,
        "font-style": font_style,
        "fill": fill,
        "text-anchor": text_anchor,
    }
    style = serialize_style(style_parts)

    obj_id = generate_id("text")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "text",
        "text": text,
        "x": x,
        "y": y,
        "font_family": font_family,
        "font_size": font_size,
        "font_weight": font_weight,
        "font_style": font_style,
        "fill": fill,
        "text_anchor": text_anchor,
        "line_height": line_height,
        "style": style,
        "transform": "",
        "layer": _default_layer_id(project),
    }
    if box_width is not None:
        obj["box_width"] = box_width
    if box_height is not None:
        obj["box_height"] = box_height
    if layer:
        obj["layer"] = layer

    _add_object(project, obj)
    return obj


def _rebuild_text_style(obj: Dict[str, Any]) -> None:
    """Rebuild the style string from object properties."""
    style_parts = {}
    if "font_family" in obj:
        style_parts["font-family"] = obj["font_family"]
    if "font_size" in obj:
        style_parts["font-size"] = f"{obj['font_size']}px"
    if "font_weight" in obj:
        style_parts["font-weight"] = obj["font_weight"]
    if "font_style" in obj:
        style_parts["font-style"] = obj["font_style"]
    if "fill" in obj:
        style_parts["fill"] = obj["fill"]
    if "text_anchor" in obj:
        style_parts["text-anchor"] = obj["text_anchor"]
    if "opacity" in obj:
        style_parts["opacity"] = str(obj["opacity"])
    if "text_decoration" in obj:
        style_parts["text-decoration"] = obj["text_decoration"]
    if "letter_spacing" in obj:
        style_parts["letter-spacing"] = f"{obj['letter_spacing']}px"
    if "word_spacing" in obj:
        style_parts["word-spacing"] = f"{obj['word_spacing']}px"
    if "line_height" in obj:
        style_parts["line-height"] = str(obj["line_height"])
    if "stroke" in obj:
        style_parts["stroke"] = obj["stroke"]

    obj["style"] = serialize_style(style_parts)
