# ruff: noqa: F403, F405, E501
from .import_mod_base import *  # noqa: F403


def _validate_path(path: str, label: str = "path") -> str:
    """Validate that *path* is a non-empty string and return it stripped."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return path.strip()


def _detect_format(path: str) -> str:
    """Detect the canonical format from a file extension.

    Returns
    -------
    str
        The canonical format key (e.g. ``"step"``, ``"stl"``).

    Raises
    ------
    ValueError
        If the extension is not recognised.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXT_MAP:
        raise ValueError(
            f"Cannot detect format from extension '{ext}'. "
            f"Supported extensions: {', '.join(sorted(EXT_MAP))}"
        )
    return EXT_MAP[ext]


def _next_part_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for parts."""
    items = project.get("parts", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _next_mesh_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for meshes."""
    items = project.get("meshes", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _next_draft_id(project: Dict[str, Any]) -> int:
    """Return the next available integer ID for draft objects."""
    items = project.get("draft_objects", [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str, key: str) -> str:
    """Return a unique name derived from *base* inside ``project[key]``."""
    existing = {item["name"] for item in project.get(key, [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _default_name(
    path: str, name: Optional[str], project: Dict[str, Any], key: str
) -> str:
    """Derive a name from *path* if *name* is None, then make it unique."""
    if name is not None:
        return name
    base = os.path.splitext(os.path.basename(path))[0]
    return _unique_name(project, base, key)


def _import_as_part(
    project: Dict[str, Any],
    path: str,
    fmt: str,
    name: Optional[str] = None,
    import_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an imported part entry in ``project["parts"]``."""
    parts = ensure_collection(project, "parts")
    label = _default_name(path, name, project, "parts")

    part: Dict[str, Any] = {
        "id": _next_part_id(project),
        "name": label,
        "type": "imported",
        "params": {
            "source_path": path,
            "source_format": fmt,
            "import_params": import_params or {},
        },
        "placement": {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
        },
        "material_index": None,
        "visible": True,
    }

    parts.append(part)
    return part


def _import_as_mesh(
    project: Dict[str, Any],
    path: str,
    fmt: str,
    name: Optional[str] = None,
    import_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an imported mesh entry in ``project["meshes"]``."""
    meshes = ensure_collection(project, "meshes")
    label = _default_name(path, name, project, "meshes")

    mesh: Dict[str, Any] = {
        "id": _next_mesh_id(project),
        "name": label,
        "source": path,
        "format": fmt,
        "vertices_count": 0,
        "faces_count": 0,
        "operations_applied": [],
    }

    meshes.append(mesh)
    return mesh
