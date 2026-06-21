# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


def _locked_save_json(path: str, data: dict, **dump_kwargs) -> None:
    """Atomically write JSON with exclusive file locking."""
    path = os.path.abspath(path)
    try:
        f = open(path, "r+")  # no truncation on open
    except FileNotFoundError:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        f = open(path, "w")  # first save — file doesn't exist yet
    with f:
        _locked = False
        try:
            if _HAS_FCNTL:
                _fcntl.flock(f.fileno(), _fcntl.LOCK_EX)
                _locked = True
        except OSError:
            pass  # unsupported FS — proceed unlocked
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2, **dump_kwargs)
            f.flush()
        finally:
            if _locked:
                _fcntl.flock(f.fileno(), _fcntl.LOCK_UN)


def _default_project(name: str = "untitled") -> dict:
    """Return a fresh project structure."""
    return {
        "version": "1.0",
        "name": name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "clouds": [],  # list of cloud entries
        "meshes": [],  # list of mesh entries
        "settings": {
            "cloud_export_format": "LAS",
            "cloud_export_ext": "las",
            "mesh_export_format": "OBJ",
            "mesh_export_ext": "obj",
            "global_shift": None,  # [x, y, z] or null
            "no_timestamp": True,
        },
        "history": [],  # operation history for undo
    }


def _cloud_entry(path: str, label: Optional[str] = None) -> dict:
    """Create a cloud entry dict."""
    path = os.path.abspath(path)
    return {
        "path": path,
        "label": label or Path(path).stem,
        "loaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "scalar_fields": [],
        "has_normals": False,
        "has_rgb": False,
    }


def _mesh_entry(path: str, label: Optional[str] = None) -> dict:
    """Create a mesh entry dict."""
    path = os.path.abspath(path)
    return {
        "path": path,
        "label": label or Path(path).stem,
        "loaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def create_project(output_path: str, name: Optional[str] = None) -> dict:
    """Create a new empty project and save it to disk.

    Args:
        output_path: Where to save the .json project file.
        name: Human-readable project name.

    Returns:
        The project dict.
    """
    output_path = os.path.abspath(output_path)
    if name is None:
        name = Path(output_path).stem
    proj = _default_project(name)
    _locked_save_json(output_path, proj)
    return proj


def load_project(path: str) -> dict:
    """Load a project from disk.

    Args:
        path: Path to the .json project file.

    Returns:
        The project dict.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is not a valid project JSON.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    if "version" not in data or "clouds" not in data:
        raise ValueError(f"Not a valid CloudCompare CLI project: {path}")

    return data


def save_project(project: dict, path: str) -> None:
    """Save project to disk.

    Args:
        project: Project dict.
        path: Destination .json file path.
    """
    project["modified_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _locked_save_json(path, project)


def add_cloud(project: dict, cloud_path: str, label: Optional[str] = None) -> dict:
    """Add a cloud to the project's cloud list.

    Args:
        project: Project dict (modified in place).
        cloud_path: Path to the cloud file.
        label: Optional label.

    Returns:
        The new cloud entry.
    """
    if not os.path.exists(cloud_path):
        raise FileNotFoundError(f"Cloud file not found: {cloud_path}")

    entry = _cloud_entry(cloud_path, label)
    project["clouds"].append(entry)
    return entry
