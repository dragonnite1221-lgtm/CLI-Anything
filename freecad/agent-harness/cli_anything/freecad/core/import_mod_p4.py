# ruff: noqa: F403, F405, E501
from .import_mod_base import *  # noqa: F403

# fmt: off
from .import_mod_p1 import _import_as_mesh, _validate_path  # noqa: E402,E501
# fmt: on


def import_3mf(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a 3MF file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the 3MF file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "3mf", name)


def import_ply(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a PLY file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the PLY file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "ply", name)


def import_off(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import an OFF file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the OFF file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "off", name)


def import_gltf(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a glTF/GLB file into ``project["meshes"]``.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Path to the glTF or GLB file.
    name : str or None
        Label for the imported mesh.

    Returns
    -------
    dict
        The newly created mesh entry.
    """
    path = _validate_path(path)
    return _import_as_mesh(project, path, "gltf", name)
