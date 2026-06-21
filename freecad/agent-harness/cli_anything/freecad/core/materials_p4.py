# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403

# fmt: off
from .materials_p2 import MATERIAL_PROPS, PRESETS, _next_id  # noqa: E402,E501
from .materials_p3 import _unique_name, _validate_color, _validate_project  # noqa: E402,E501
# fmt: on


def create_material(
    project: Dict[str, Any],
    name: str = "Material",
    preset: Optional[str] = None,
    color: Optional[List[float]] = None,
    metallic: float = 0.0,
    roughness: float = 0.5,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create a new material, optionally based on a preset.

    When *preset* is given, its ``color``, ``metallic``, and ``roughness``
    values are used as defaults.  Explicit *color*, *metallic*, and
    *roughness* arguments override the preset values.

    Parameters
    ----------
    project:
        The project dictionary.
    name:
        Material display name.
    preset:
        Optional preset key from :data:`PRESETS`.
    color:
        Base color ``[R, G, B, A]`` with components in ``[0, 1]``.
    metallic:
        Metallic factor ``[0, 1]``.
    roughness:
        Roughness factor ``[0, 1]``.
    **kwargs:
        Optional engineering properties: ``density``, ``youngs_modulus``,
        ``poisson_ratio``, ``thermal_conductivity``, ``specific_heat``,
        ``yield_strength``, ``ultimate_strength``.

    Returns
    -------
    Dict[str, Any]
        The newly created material dictionary.

    Raises
    ------
    ValueError
        If the preset is unknown, colour is invalid, or numeric values are
        out of range.
    """
    _validate_project(project)

    # Resolve preset defaults
    preset_data: Dict[str, Any] = {}
    if preset is not None:
        if preset not in PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. Available presets: {', '.join(sorted(PRESETS))}"
            )
        preset_data = PRESETS[preset]
        # Use preset name as the material name if caller left the default
        if name == "Material":
            name = preset.replace("_", " ").title()

    # Determine final values (explicit args override preset)
    final_color: List[float]
    if color is not None:
        final_color = _validate_color(color)
    elif "color" in preset_data:
        final_color = list(preset_data["color"])
    else:
        final_color = [0.8, 0.8, 0.8, 1.0]

    final_metallic = metallic
    if preset_data and metallic == 0.0 and "metallic" in preset_data:
        # Only use preset metallic when caller left the default
        final_metallic = preset_data["metallic"]
    final_metallic = float(final_metallic)

    final_roughness = roughness
    if preset_data and roughness == 0.5 and "roughness" in preset_data:
        final_roughness = preset_data["roughness"]
    final_roughness = float(final_roughness)

    if not 0.0 <= final_metallic <= 1.0:
        raise ValueError(f"Metallic must be 0.0-1.0, got {final_metallic}")
    if not 0.0 <= final_roughness <= 1.0:
        raise ValueError(f"Roughness must be 0.0-1.0, got {final_roughness}")

    mat_name = _unique_name(project, name)

    mat: Dict[str, Any] = {
        "id": _next_id(project),
        "name": mat_name,
        "preset": preset,
        "color": final_color,
        "metallic": final_metallic,
        "roughness": final_roughness,
        "assigned_to": [],
    }

    # Engineering properties from preset (as defaults) and kwargs (overrides)
    _ENG_PROPS = (
        "density",
        "youngs_modulus",
        "poisson_ratio",
        "thermal_conductivity",
        "specific_heat",
        "yield_strength",
        "ultimate_strength",
    )
    for ep in _ENG_PROPS:
        value = kwargs.get(ep)
        if value is None and preset_data:
            value = preset_data.get(ep)
        if value is not None:
            value = float(value)
            spec = MATERIAL_PROPS.get(ep, {})
            if spec.get("min") is not None and value < spec["min"]:
                raise ValueError(
                    f"Property '{ep}' minimum is {spec['min']}, got {value}"
                )
            if spec.get("max") is not None and value > spec["max"]:
                raise ValueError(
                    f"Property '{ep}' maximum is {spec['max']}, got {value}"
                )
            mat[ep] = value

    project["materials"].append(mat)
    return mat
