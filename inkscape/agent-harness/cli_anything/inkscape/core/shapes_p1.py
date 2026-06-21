# ruff: noqa: F403, F405, E501
from .shapes_base import *  # noqa: F403


def _default_layer_id(project: Dict[str, Any]) -> str:
    """Get the ID of the first layer, or empty string."""
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


def add_rect(
    project: Dict[str, Any],
    x: float = 0,
    y: float = 0,
    width: float = 100,
    height: float = 100,
    rx: float = 0,
    ry: float = 0,
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a rectangle to the document."""
    if width <= 0 or height <= 0:
        raise ValueError(f"Rectangle dimensions must be positive: {width}x{height}")

    obj_id = generate_id("rect")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "rect",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "rx": rx,
        "ry": ry,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def add_circle(
    project: Dict[str, Any],
    cx: float = 50,
    cy: float = 50,
    r: float = 50,
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a circle to the document."""
    if r <= 0:
        raise ValueError(f"Circle radius must be positive: {r}")

    obj_id = generate_id("circle")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "circle",
        "cx": cx,
        "cy": cy,
        "r": r,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def add_ellipse(
    project: Dict[str, Any],
    cx: float = 50,
    cy: float = 50,
    rx: float = 75,
    ry: float = 50,
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add an ellipse to the document."""
    if rx <= 0 or ry <= 0:
        raise ValueError(f"Ellipse radii must be positive: rx={rx}, ry={ry}")

    obj_id = generate_id("ellipse")
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "ellipse",
        "cx": cx,
        "cy": cy,
        "rx": rx,
        "ry": ry,
        "style": style or DEFAULT_STYLE,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj


def add_line(
    project: Dict[str, Any],
    x1: float = 0,
    y1: float = 0,
    x2: float = 100,
    y2: float = 100,
    name: Optional[str] = None,
    style: Optional[str] = None,
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a line to the document."""
    obj_id = generate_id("line")
    line_style = style or "fill:none;stroke:#000000;stroke-width:2"
    obj = {
        "id": obj_id,
        "name": name or obj_id,
        "type": "line",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "style": line_style,
        "transform": "",
        "layer": layer or _default_layer_id(project),
    }
    _add_object(project, obj)
    return obj
