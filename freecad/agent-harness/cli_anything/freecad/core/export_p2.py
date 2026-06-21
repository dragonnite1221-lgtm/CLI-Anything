# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _FORMAT_VALIDATORS  # noqa: E402,E501
# fmt: on


def export_project(
    project: dict,
    output_path: str,
    preset: str = "step",
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Export a FreeCAD project to a CAD/mesh file.

    1. Generates a FreeCAD macro script via :func:`generate_macro`.
    2. Calls :func:`freecad_backend.run_macro` to execute it headlessly.
    3. Verifies the output file exists and has the correct format.

    Parameters
    ----------
    project : dict
        The project JSON state containing parts, bodies, and placements.
    output_path : str
        Destination file path for the exported geometry.
    preset : str
        Name of an export preset (see ``EXPORT_PRESETS``).
    overwrite : bool
        If *False* (default), raise ``FileExistsError`` when *output_path*
        already exists.

    Returns
    -------
    dict
        ``{"output": str, "format": str, "file_size": int,
        "method": "freecad-headless"}``

    Raises
    ------
    FileExistsError
        If *output_path* exists and *overwrite* is False.
    ValueError
        If *preset* is not a known preset name.
    RuntimeError
        If the macro execution fails or the output file is missing/invalid.
    """
    output_path = os.path.abspath(output_path)

    if not overwrite and os.path.exists(output_path):
        raise FileExistsError(
            f"Output file already exists: {output_path}. "
            "Set overwrite=True to replace it."
        )

    if preset not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown export preset '{preset}'. "
            f"Available presets: {', '.join(sorted(EXPORT_PRESETS))}"
        )

    preset_config = EXPORT_PRESETS[preset]
    export_format = preset_config["format"]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Generate the FreeCAD macro script
    macro_content = generate_macro(project, output_path, export_format=export_format)

    # Execute via the headless backend
    result = freecad_backend.export_headless(
        macro_content,
        output_path,
        timeout=120,
    )

    # Verify the output file
    if not os.path.isfile(output_path):
        raise RuntimeError(
            f"Export failed: output file was not created at {output_path}. "
            f"Backend result: {result}"
        )

    # Run format-specific validation if available
    validator = _FORMAT_VALIDATORS.get(export_format)
    if validator and not validator(output_path):
        raise RuntimeError(
            f"Export produced an invalid {export_format.upper()} file at "
            f"{output_path}. The file header does not match the expected format."
        )

    ext = _FORMAT_EXTENSIONS.get(export_format, f".{export_format}")
    file_size = os.path.getsize(output_path)

    return {
        "output": output_path,
        "format": ext.lstrip("."),
        "file_size": file_size,
        "method": "freecad-headless",
    }


def get_export_info(project: dict) -> Dict[str, Any]:
    """Return a summary of what will be exported from *project*.

    Parameters
    ----------
    project : dict
        The project JSON state.

    Returns
    -------
    dict
        Summary with keys ``part_count``, ``body_count``,
        ``boolean_op_count``, ``available_presets``, and ``part_names``.
    """
    parts = project.get("parts", [])
    bodies = project.get("bodies", [])
    boolean_ops = project.get("boolean_ops", [])

    part_names = [p.get("name", "Unnamed") for p in parts]

    return {
        "part_count": len(parts),
        "body_count": len(bodies),
        "boolean_op_count": len(boolean_ops),
        "part_names": part_names,
        "available_presets": list(EXPORT_PRESETS.keys()),
    }
