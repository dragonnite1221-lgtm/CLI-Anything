# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403

# fmt: off
from .project_p1 import _find_layer, _touch_modified  # noqa: E402,E501
# fmt: on


def project_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """Return summary info about the project.

    Returns
    -------
    dict
        A lightweight summary suitable for display.
    """
    canvas = project.get("canvas", {})
    layers = project.get("layers", [])
    return {
        "name": project.get("name", "untitled"),
        "version": project.get("version", "unknown"),
        "created": project.get("created"),
        "modified": project.get("modified"),
        "canvas": {
            "width": canvas.get("width"),
            "height": canvas.get("height"),
            "colorspace": canvas.get("colorspace", "RGBA"),
            "depth": canvas.get("depth", "U8"),
            "resolution": canvas.get("resolution", 300),
            "profile": canvas.get("profile"),
        },
        "layer_count": len(layers),
        "layers_summary": [
            {
                "name": ly.get("name"),
                "type": ly.get("type"),
                "visible": ly.get("visible", True),
                "opacity": ly.get("opacity", 255),
                "blending_mode": ly.get("blending_mode", "normal"),
                "filter_count": len(ly.get("filters", [])),
            }
            for ly in layers
        ],
        "metadata": project.get("metadata", {}),
    }


def add_layer(
    project: Dict[str, Any],
    name: str,
    layer_type: str = "paintlayer",
    opacity: int = 255,
    visible: bool = True,
    blending_mode: str = "normal",
) -> Dict[str, Any]:
    """Add a layer to the project's layer stack.

    Parameters
    ----------
    project : dict
        The project to modify (mutated in-place and returned).
    name : str
        Layer name (must be unique within the stack).
    layer_type : str
        One of: paintlayer, grouplayer, vectorlayer, filterlayer,
        filllayer, clonelayer, filelayer.
    opacity : int
        Layer opacity 0-255.
    visible : bool
        Whether the layer is visible.
    blending_mode : str
        Blending / compositing mode name.

    Returns
    -------
    dict
        The updated project.
    """
    if layer_type not in VALID_LAYER_TYPES:
        raise ValueError(
            f"Invalid layer type '{layer_type}'. "
            f"Choose from: {', '.join(VALID_LAYER_TYPES)}"
        )
    if not 0 <= opacity <= 255:
        raise ValueError(f"Opacity must be 0-255, got {opacity}")
    if _find_layer(project, name) is not None:
        raise ValueError(f"A layer named '{name}' already exists")

    layer: Dict[str, Any] = {
        "name": name,
        "type": layer_type,
        "opacity": opacity,
        "visible": visible,
        "blending_mode": blending_mode,
        "locked": False,
        "filters": [],
    }
    project.setdefault("layers", []).append(layer)
    _touch_modified(project)
    return project


def remove_layer(project: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Remove a layer by name.

    Parameters
    ----------
    project : dict
        The project to modify.
    name : str
        Name of the layer to remove.

    Returns
    -------
    dict
        The updated project.

    Raises
    ------
    KeyError
        If no layer with the given name exists.
    """
    layers: List[dict] = project.get("layers", [])
    for i, layer in enumerate(layers):
        if layer["name"] == name:
            layers.pop(i)
            _touch_modified(project)
            return project
    raise KeyError(f"Layer not found: '{name}'")


def list_layers(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return list of layers with their properties.

    Returns
    -------
    list[dict]
        Each element is a copy of the layer dictionary.
    """
    return [dict(ly) for ly in project.get("layers", [])]
