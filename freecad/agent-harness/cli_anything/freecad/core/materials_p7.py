# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403

# fmt: off
from .materials_p3 import _get_material, _validate_project  # noqa: E402,E501
from .materials_p4 import create_material  # noqa: E402,E501
# fmt: on


def import_material(project: Dict[str, Any], path: str) -> Dict[str, Any]:
    """Load a material from a JSON file and add it to the project.

    The JSON file should contain keys such as ``name``, ``color``,
    ``metallic``, ``roughness``, and optional engineering properties.

    Parameters
    ----------
    project:
        The project dictionary.
    path:
        Path to a JSON file describing the material.

    Returns
    -------
    Dict[str, Any]
        The newly created material dictionary.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If the JSON is invalid or material properties are out of range.
    """
    _validate_project(project)

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Material JSON must be an object, got {type(data).__name__}")

    # Extract recognised kwargs for create_material
    create_kwargs: Dict[str, Any] = {}
    for ep in (
        "density",
        "youngs_modulus",
        "poisson_ratio",
        "thermal_conductivity",
        "specific_heat",
        "yield_strength",
        "ultimate_strength",
    ):
        if ep in data:
            create_kwargs[ep] = data[ep]

    return create_material(
        project,
        name=data.get("name", "Imported Material"),
        preset=data.get("preset"),
        color=data.get("color"),
        metallic=float(data.get("metallic", 0.0)),
        roughness=float(data.get("roughness", 0.5)),
        **create_kwargs,
    )


def export_material(project: Dict[str, Any], index: int, path: str) -> Dict[str, Any]:
    """Save a material to a JSON file.

    Parameters
    ----------
    project:
        The project dictionary.
    index:
        Material index.
    path:
        Destination file path.

    Returns
    -------
    Dict[str, Any]
        Summary with ``path`` and ``material_name``.

    Raises
    ------
    IndexError
        If *index* is out of range.
    """
    _validate_project(project)
    mat = _get_material(project, index)

    # Build a clean export dict (omit internal bookkeeping)
    export_data: Dict[str, Any] = {}
    for key in (
        "name",
        "color",
        "metallic",
        "roughness",
        "preset",
        "density",
        "youngs_modulus",
        "poisson_ratio",
        "thermal_conductivity",
        "specific_heat",
        "yield_strength",
        "ultimate_strength",
    ):
        if key in mat:
            export_data[key] = mat[key]

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(export_data, fh, indent=2)

    return {"path": path, "material_name": mat.get("name", f"Material {index}")}
