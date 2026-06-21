# ruff: noqa: F403, F405, E501
from .import_mod_base import *  # noqa: F403

# fmt: off
from .import_mod_p1 import _import_as_mesh, _import_as_part, _validate_path  # noqa: E402,E501
from .import_mod_p2 import _import_as_draft  # noqa: E402,E501
# fmt: on


def import_stl(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import an STL file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the STL file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "stl", name)


def import_obj(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import an OBJ file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the OBJ file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "obj", name)


def import_dxf(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a DXF file into ``project["draft_objects"]`` or ``project["parts"]``.

    DXF files primarily contain 2D geometry and are imported as draft
    objects by default.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the DXF file.
    name : str or None
        Label for the imported object.

    Returns
    -------
    dict
        The newly created draft object entry.
    """
    path = _validate_path(path)
    return _import_as_draft(project, path, "dxf", name)


def import_svg(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import an SVG file into ``project["draft_objects"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the SVG file.
    name : str or None
        Label for the imported object.

    Returns
    -------
    dict
        The newly created draft object entry.
    """
    path = _validate_path(path)
    return _import_as_draft(project, path, "svg", name)


def import_brep(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a BREP file into ``project["parts"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the BREP file.
    name : str or None
        Label for the imported part.

    Returns
    -------
    dict
        The newly created part entry.
    """
    path = _validate_path(path)
    return _import_as_part(project, path, "brep", name)
