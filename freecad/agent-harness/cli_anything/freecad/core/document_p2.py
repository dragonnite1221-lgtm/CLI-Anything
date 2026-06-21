# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403

# fmt: off
from .document_p1 import ALL_COLLECTIONS, _now_iso, _validate_project  # noqa: E402,E501
# fmt: on


def open_document(path: str) -> Dict[str, Any]:
    """Load a project document from a JSON file.

    Parameters
    ----------
    path:
        Filesystem path to the ``.json`` project file.

    Returns
    -------
    Dict[str, Any]
        The validated project dictionary.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If the file cannot be parsed or fails validation.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Project file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            project = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse project file: {exc}") from exc

    if not isinstance(project, dict):
        raise ValueError("Project file must contain a JSON object at the top level")

    _validate_project(project)
    return project


def save_document(project: Dict[str, Any], path: str) -> str:
    """Save a project document to a JSON file.

    The ``metadata.modified`` timestamp is updated automatically before
    writing.

    Parameters
    ----------
    project:
        The project dictionary to persist.
    path:
        Destination file path.

    Returns
    -------
    str
        The absolute path of the saved file.

    Raises
    ------
    ValueError
        If the project fails validation or *path* is invalid.
    OSError
        If the file cannot be written.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Path must be a non-empty string")

    _validate_project(project)

    project["metadata"]["modified"] = _now_iso()

    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(project, fh, indent=2, ensure_ascii=False)

    return os.path.abspath(path)


def get_document_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """Return a concise summary of a project document.

    Parameters
    ----------
    project:
        A valid project dictionary.

    Returns
    -------
    Dict[str, Any]
        Summary containing name, units, and collection counts.

    Raises
    ------
    ValueError
        If the project fails validation.
    """
    _validate_project(project)

    info = {
        "name": project["name"],
        "units": project["units"],
        "version": project["version"],
    }
    for col in ALL_COLLECTIONS:
        info[f"{col}_count"] = len(project.get(col, []))
    info["metadata"] = project.get("metadata", {})
    return info


def list_profiles() -> List[Dict[str, Any]]:
    """Return a list of available project profiles.

    Each entry contains the profile ``name``, ``units``, and
    ``description``.

    Returns
    -------
    List[Dict[str, Any]]
    """
    return [
        {
            "name": key,
            "units": value["units"],
            "description": value["description"],
        }
        for key, value in PROFILES.items()
    ]
