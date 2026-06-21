# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403

# fmt: off
from .materials_p1 import PRESETS  # noqa: E402,E501
from .materials_p2 import MATERIAL_PROPS, _get_material, _validate_color, _validate_project  # noqa: E402,E501
# fmt: on


def set_material_property(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> None:
    """Set a single property on a material.

    Parameters
    ----------
    project:
        The project dictionary.
    index:
        Material index.
    prop:
        Property name.  One of ``"color"``, ``"metallic"``, ``"roughness"``,
        or ``"name"``.
    value:
        New value.  Type depends on the property.

    Raises
    ------
    IndexError
        If *index* is out of range.
    ValueError
        If *prop* is unknown or *value* is invalid.
    """
    _validate_project(project)
    mat = _get_material(project, index)

    if prop not in MATERIAL_PROPS:
        raise ValueError(
            f"Unknown material property: '{prop}'. "
            f"Valid properties: {', '.join(sorted(MATERIAL_PROPS))}"
        )

    spec = MATERIAL_PROPS[prop]
    ptype = spec["type"]

    if ptype == "float":
        value = float(value)
        if "min" in spec and value < spec["min"]:
            raise ValueError(f"Property '{prop}' minimum is {spec['min']}, got {value}")
        if "max" in spec and value > spec["max"]:
            raise ValueError(f"Property '{prop}' maximum is {spec['max']}, got {value}")
        mat[prop] = value
    elif ptype == "color4":
        if isinstance(value, str):
            value = [float(x.strip()) for x in value.split(",")]
        mat[prop] = _validate_color(value)
    elif ptype == "str":
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Property '{prop}' must be a non-empty string")
        mat[prop] = value.strip()
    else:
        mat[prop] = value


def list_presets() -> List[Dict[str, Any]]:
    """Return a list of all available material presets.

    Returns
    -------
    List[Dict[str, Any]]
        Each entry contains the preset ``name``, ``color``, ``metallic``,
        ``roughness``, and any engineering properties.
    """
    results: List[Dict[str, Any]] = []
    for key, value in PRESETS.items():
        entry: Dict[str, Any] = {
            "name": key,
            "color": list(value["color"]),
            "metallic": value["metallic"],
            "roughness": value["roughness"],
        }
        for ep in (
            "density",
            "youngs_modulus",
            "poisson_ratio",
            "thermal_conductivity",
            "specific_heat",
            "yield_strength",
            "ultimate_strength",
        ):
            if ep in value:
                entry[ep] = value[ep]
        results.append(entry)
    return results
