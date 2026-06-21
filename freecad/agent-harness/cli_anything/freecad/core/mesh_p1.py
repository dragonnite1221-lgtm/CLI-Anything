# ruff: noqa: F403, F405, E501
from .mesh_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for meshes."""
    items = project.get("meshes", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    """Return a unique name derived from *base* inside ``project["meshes"]``."""
    existing = {item["name"] for item in project.get("meshes", [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _get_mesh(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return the mesh at *index*, raising ``IndexError`` if out of range."""
    meshes = project.get("meshes", [])
    if not isinstance(index, int) or index < 0 or index >= len(meshes):
        raise IndexError(f"Mesh index {index} out of range (0..{len(meshes) - 1})")
    return meshes[index]


def _validate_path(path: str, label: str = "path") -> str:
    """Validate that *path* is a non-empty string and return it normalised."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return path.strip()


def import_mesh(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Import a mesh file and register it in ``project["meshes"]``.

    The actual file loading happens during macro generation; this function
    records the import intent and metadata.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    path : str
        Filesystem path to the mesh file.
    name : str or None
        Human-readable label.  Derived from filename when *None*.

    Returns
    -------
    dict
        The newly created mesh entry.

    Raises
    ------
    ValueError
        If *path* is empty.
    """
    path = _validate_path(path)
    meshes = ensure_collection(project, "meshes")

    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if name is None:
        base = os.path.splitext(os.path.basename(path))[0]
        name = _unique_name(project, base)

    mesh: Dict[str, Any] = {
        "id": _next_id(project),
        "name": name,
        "source": path,
        "format": ext if ext else "unknown",
        "vertices_count": 0,
        "faces_count": 0,
        "operations_applied": [],
    }

    meshes.append(mesh)
    return mesh
