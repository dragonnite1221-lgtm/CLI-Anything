# ruff: noqa: F403, F405, E501
from .import_mod_base import *  # noqa: F403

# fmt: off
from .import_mod_p1 import _default_name, _detect_format, _import_as_mesh, _import_as_part, _next_draft_id, _validate_path  # noqa: E402,E501
# fmt: on


def _import_as_draft(
    project: Dict[str, Any],
    path: str,
    fmt: str,
    name: Optional[str] = None,
    import_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an imported draft object entry in ``project["draft_objects"]``."""
    objs = ensure_collection(project, "draft_objects")
    label = _default_name(path, name, project, "draft_objects")

    draft_obj: Dict[str, Any] = {
        "id": _next_draft_id(project),
        "name": label,
        "type": "imported",
        "properties": {
            "source_path": path,
            "source_format": fmt,
            "import_params": import_params or {},
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "visible": True,
    }

    objs.append(draft_obj)
    return draft_obj


def import_file(
    project: Dict[str, Any],
    path: str,
    format: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a file, auto-detecting the format from its extension.

    Depending on the detected format the imported geometry is placed in
    ``project["parts"]``, ``project["meshes"]``, or
    ``project["draft_objects"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Filesystem path to the file.
    format : str or None
        Explicit format override.  When *None* the format is detected
        from the file extension.
    name : str or None
        Label for the imported object.  Derived from filename when *None*.

    Returns
    -------
    dict
        The newly created import entry.

    Raises
    ------
    ValueError
        If the format cannot be detected or is unsupported.
    """
    path = _validate_path(path)
    fmt = format.lower() if format else _detect_format(path)

    if fmt in PART_FORMATS or fmt in {"step", "iges", "brep"}:
        return _import_as_part(project, path, fmt, name)
    elif fmt in MESH_FORMATS:
        return _import_as_mesh(project, path, fmt, name)
    elif fmt in DRAFT_FORMATS:
        return _import_as_draft(project, path, fmt, name)
    else:
        raise ValueError(
            f"Unsupported format '{fmt}'. Supported: "
            f"{', '.join(sorted(PART_FORMATS | MESH_FORMATS | DRAFT_FORMATS))}"
        )


def import_step(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a STEP file into ``project["parts"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the STEP file.
    name : str or None
        Label for the imported part.

    Returns
    -------
    dict
        The newly created part entry.
    """
    path = _validate_path(path)
    return _import_as_part(project, path, "step", name)


def import_iges(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import an IGES file into ``project["parts"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the IGES file.
    name : str or None
        Label for the imported part.

    Returns
    -------
    dict
        The newly created part entry.
    """
    path = _validate_path(path)
    return _import_as_part(project, path, "iges", name)
