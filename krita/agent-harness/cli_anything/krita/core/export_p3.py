# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p2 import build_kra_from_project  # noqa: E402,E501
# fmt: on


def export_image(
    project: dict,
    output_path: str,
    preset: str = "png",
    overwrite: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Export a project to an image file.

    1. Builds a ``.kra`` file from the project JSON state.
    2. Calls the Krita backend to convert to the target format.

    Parameters
    ----------
    project : dict
        The project JSON state.
    output_path : str
        Destination file path for the exported image.
    preset : str
        Name of an export preset (see ``EXPORT_PRESETS``).
    overwrite : bool
        If *False* (default), raise ``FileExistsError`` when *output_path*
        already exists.
    **kwargs
        Extra options forwarded to the backend export call.

    Returns
    -------
    dict
        ``{"output_path": str, "file_size": int, "format": str, "method": str}``

    Raises
    ------
    FileExistsError
        If *output_path* exists and *overwrite* is False.
    ValueError
        If *preset* is not a known preset name.
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
    export_options = {**preset_config.get("options", {}), **kwargs}

    # Build a temporary .kra from the project state
    tmp_dir = tempfile.mkdtemp(prefix="krita_export_")
    kra_path = os.path.join(tmp_dir, "project.kra")
    build_kra_from_project(project, kra_path)

    # Use the Krita backend to export
    method = "krita_backend"
    try:
        export_file(
            input_path=kra_path,
            output_path=output_path,
            export_options=export_options,
        )
    except Exception:
        # Re-raise so callers can handle backend failures
        raise

    file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

    return {
        "output_path": output_path,
        "file_size": file_size,
        "format": preset_config["extension"],
        "method": method,
    }
