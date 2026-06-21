# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403

# fmt: off
from .project_p1 import _mesh_entry  # noqa: E402,E501
# fmt: on


def add_mesh(project: dict, mesh_path: str, label: Optional[str] = None) -> dict:
    """Add a mesh to the project's mesh list.

    Args:
        project: Project dict (modified in place).
        mesh_path: Path to the mesh file.
        label: Optional label.

    Returns:
        The new mesh entry.
    """
    if not os.path.exists(mesh_path):
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")

    entry = _mesh_entry(mesh_path, label)
    project["meshes"].append(entry)
    return entry


def remove_cloud(project: dict, index: int) -> dict:
    """Remove a cloud by index.

    Args:
        project: Project dict (modified in place).
        index: 0-based index of the cloud to remove.

    Returns:
        The removed cloud entry.
    """
    if index < 0 or index >= len(project["clouds"]):
        raise IndexError(
            f"No cloud at index {index} (project has {len(project['clouds'])} clouds)"
        )
    return project["clouds"].pop(index)


def remove_mesh(project: dict, index: int) -> dict:
    """Remove a mesh by index.

    Args:
        project: Project dict (modified in place).
        index: 0-based index of the mesh to remove.

    Returns:
        The removed mesh entry.
    """
    if index < 0 or index >= len(project["meshes"]):
        raise IndexError(
            f"No mesh at index {index} (project has {len(project['meshes'])} meshes)"
        )
    return project["meshes"].pop(index)


def get_cloud(project: dict, index: int) -> dict:
    """Get a cloud entry by index.

    Args:
        project: Project dict.
        index: 0-based index.

    Returns:
        The cloud entry dict.
    """
    clouds = project.get("clouds", [])
    if index < 0 or index >= len(clouds):
        raise IndexError(f"No cloud at index {index}")
    return clouds[index]


def get_mesh(project: dict, index: int) -> dict:
    """Get a mesh entry by index."""
    meshes = project.get("meshes", [])
    if index < 0 or index >= len(meshes):
        raise IndexError(f"No mesh at index {index}")
    return meshes[index]


def project_info(project: dict) -> dict:
    """Return a summary dict of the project state."""
    return {
        "name": project.get("name", "unnamed"),
        "version": project.get("version", "?"),
        "created_at": project.get("created_at", ""),
        "modified_at": project.get("modified_at", ""),
        "cloud_count": len(project.get("clouds", [])),
        "mesh_count": len(project.get("meshes", [])),
        "history_depth": len(project.get("history", [])),
        "settings": project.get("settings", {}),
        "clouds": [
            {"index": i, "label": c["label"], "path": c["path"]}
            for i, c in enumerate(project.get("clouds", []))
        ],
        "meshes": [
            {"index": i, "label": m["label"], "path": m["path"]}
            for i, m in enumerate(project.get("meshes", []))
        ],
    }


def record_operation(
    project: dict, operation: str, inputs: list[str], outputs: list[str], params: dict
) -> None:
    """Record an operation in the project history.

    Args:
        project: Project dict (modified in place).
        operation: Operation name (e.g., 'subsample').
        inputs: List of input file paths.
        outputs: List of output file paths.
        params: Operation parameters dict.
    """
    entry = {
        "operation": operation,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "inputs": inputs,
        "outputs": outputs,
        "params": params,
    }
    project.setdefault("history", []).append(entry)
