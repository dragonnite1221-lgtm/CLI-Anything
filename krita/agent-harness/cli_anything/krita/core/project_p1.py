# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _find_layer(project: dict, name: str) -> Optional[dict]:
    """Find a layer by name in the project's layer stack."""
    for layer in project.get("layers", []):
        if layer["name"] == name:
            return layer
    return None


def _touch_modified(project: dict) -> None:
    """Update the 'modified' timestamp on the project."""
    project["modified"] = _now_iso()


def create_project(
    name: str,
    width: int = 1920,
    height: int = 1080,
    colorspace: str = "RGBA",
    depth: str = "U8",
    resolution: int = 300,
    profile: str = "sRGB-elle-V2-srgbtrc.icc",
) -> Dict[str, Any]:
    """Create a new project JSON with image settings.

    Parameters
    ----------
    name : str
        Project name.
    width, height : int
        Canvas dimensions in pixels.
    colorspace : str
        Colour model (RGBA, RGB, GRAYA, GRAY, CMYKA, CMYK).
    depth : str
        Bit depth (U8, U16, F16, F32).
    resolution : int
        Pixels per inch.
    profile : str
        ICC colour profile filename.

    Returns
    -------
    dict
        The new project dictionary.
    """
    if colorspace not in VALID_COLORSPACES:
        raise ValueError(
            f"Invalid colorspace '{colorspace}'. "
            f"Choose from: {', '.join(VALID_COLORSPACES)}"
        )
    if depth not in VALID_DEPTHS:
        raise ValueError(
            f"Invalid depth '{depth}'. Choose from: {', '.join(VALID_DEPTHS)}"
        )
    if width < 1 or height < 1:
        raise ValueError(f"Canvas dimensions must be positive: {width}x{height}")
    if resolution < 1:
        raise ValueError(f"Resolution must be positive: {resolution}")

    now = _now_iso()
    project: Dict[str, Any] = {
        "name": name,
        "version": PROJECT_VERSION,
        "created": now,
        "modified": now,
        "canvas": {
            "width": width,
            "height": height,
            "colorspace": colorspace,
            "depth": depth,
            "resolution": resolution,
            "profile": profile,
        },
        "layers": [
            {
                "name": "Background",
                "type": "paintlayer",
                "opacity": 255,
                "visible": True,
                "blending_mode": "normal",
                "locked": False,
                "filters": [],
            }
        ],
        "metadata": {
            "author": "",
            "description": "",
            "tags": [],
        },
    }
    return project


def open_project(path: str) -> Dict[str, Any]:
    """Load a project JSON file.

    Parameters
    ----------
    path : str
        Path to the project JSON file.

    Returns
    -------
    dict
        The loaded project dictionary.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If the file does not look like a valid project.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        project = json.load(f)
    # Basic sanity checks
    if "version" not in project or "canvas" not in project:
        raise ValueError(f"Invalid project file (missing version/canvas): {path}")
    return project


def save_project(project: Dict[str, Any], path: Optional[str] = None) -> str:
    """Save project to a JSON file using atomic file locking.

    Parameters
    ----------
    project : dict
        The project dictionary to persist.
    path : str, optional
        Destination path.  If *None*, defaults to ``<project_name>.krita.json``
        in the current working directory.

    Returns
    -------
    str
        The absolute path of the saved file.
    """
    if path is None:
        safe_name = project.get("name", "untitled").replace(" ", "_")
        path = os.path.join(os.getcwd(), f"{safe_name}.krita.json")

    _touch_modified(project)
    locked_save_json(path, project, indent=2, default=str)
    return os.path.abspath(path)
