# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403

# fmt: off
from .project_p1 import _find_layer, _touch_modified  # noqa: E402,E501
# fmt: on


def set_layer_property(
    project: Dict[str, Any],
    layer_name: str,
    property_name: str,
    value: Any,
) -> Dict[str, Any]:
    """Set a property on a layer.

    Supported properties include: opacity, visible, blending_mode,
    locked, name, type.

    Parameters
    ----------
    project : dict
        The project to modify.
    layer_name : str
        Target layer.
    property_name : str
        Property key to set.
    value
        New value.

    Returns
    -------
    dict
        The updated project.
    """
    layer = _find_layer(project, layer_name)
    if layer is None:
        raise KeyError(f"Layer not found: '{layer_name}'")

    # Validate specific properties
    if property_name == "opacity" and not (0 <= int(value) <= 255):
        raise ValueError(f"Opacity must be 0-255, got {value}")
    if property_name == "type" and value not in VALID_LAYER_TYPES:
        raise ValueError(
            f"Invalid layer type '{value}'. Choose from: {', '.join(VALID_LAYER_TYPES)}"
        )

    layer[property_name] = value
    _touch_modified(project)
    return project


def add_filter(
    project: Dict[str, Any],
    layer_name: str,
    filter_name: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a filter to be applied on a layer.

    Parameters
    ----------
    project : dict
        The project to modify.
    layer_name : str
        Target layer name.
    filter_name : str
        Filter identifier (e.g. blur, sharpen, desaturate, levels, curves,
        brightness-contrast, hue-saturation, color-balance, unsharp-mask,
        posterize, threshold).
    config : dict, optional
        Filter-specific configuration parameters.

    Returns
    -------
    dict
        The updated project.
    """
    layer = _find_layer(project, layer_name)
    if layer is None:
        raise KeyError(f"Layer not found: '{layer_name}'")

    if filter_name not in VALID_FILTERS:
        raise ValueError(
            f"Unknown filter '{filter_name}'. Choose from: {', '.join(VALID_FILTERS)}"
        )

    filter_entry: Dict[str, Any] = {
        "name": filter_name,
        "config": config or {},
    }
    layer.setdefault("filters", []).append(filter_entry)
    _touch_modified(project)
    return project


def set_canvas(
    project: Dict[str, Any],
    width: Optional[int] = None,
    height: Optional[int] = None,
    resolution: Optional[int] = None,
) -> Dict[str, Any]:
    """Update canvas properties.

    Only supplied keyword arguments are changed; others are left untouched.

    Parameters
    ----------
    project : dict
        The project to modify.
    width : int, optional
        New canvas width in pixels.
    height : int, optional
        New canvas height in pixels.
    resolution : int, optional
        New resolution (ppi).

    Returns
    -------
    dict
        The updated project.
    """
    canvas = project.setdefault("canvas", {})

    if width is not None:
        if width < 1:
            raise ValueError(f"Width must be positive, got {width}")
        canvas["width"] = width

    if height is not None:
        if height < 1:
            raise ValueError(f"Height must be positive, got {height}")
        canvas["height"] = height

    if resolution is not None:
        if resolution < 1:
            raise ValueError(f"Resolution must be positive, got {resolution}")
        canvas["resolution"] = resolution

    _touch_modified(project)
    return project
