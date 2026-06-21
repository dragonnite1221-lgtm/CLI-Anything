# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403


def _now_iso() -> str:
    """Return the current local time as an ISO-8601 string."""
    return datetime.now().isoformat()


_REQUIRED_COLLECTIONS = ("parts", "sketches", "bodies", "materials")
_OPTIONAL_COLLECTIONS = (
    "assemblies",
    "meshes",
    "techdraw_pages",
    "draft_objects",
    "measurements",
    "surfaces",
    "fem_analyses",
    "cam_jobs",
    "spreadsheets",
    "motions",
)
ALL_COLLECTIONS = _REQUIRED_COLLECTIONS + _OPTIONAL_COLLECTIONS


def ensure_collection(project: Dict[str, Any], key: str) -> list:
    """Return ``project[key]``, creating it as ``[]`` if absent."""
    if key not in project:
        project[key] = []
    return project[key]


def _validate_project(project: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if *project* is missing required keys or has bad types."""
    required_keys = {
        "version",
        "name",
        "units",
        "parts",
        "sketches",
        "bodies",
        "materials",
        "metadata",
    }
    missing = required_keys - set(project.keys())
    if missing:
        raise ValueError(
            f"Project is missing required keys: {', '.join(sorted(missing))}"
        )

    if not isinstance(project["name"], str) or not project["name"]:
        raise ValueError("Project 'name' must be a non-empty string")

    if project["units"] not in VALID_UNITS:
        raise ValueError(
            f"Invalid units '{project['units']}'. Must be one of: {', '.join(sorted(VALID_UNITS))}"
        )

    for collection in _REQUIRED_COLLECTIONS:
        if not isinstance(project[collection], list):
            raise ValueError(f"Project '{collection}' must be a list")

    # Optional collections: validate type if present, but don't require
    for collection in _OPTIONAL_COLLECTIONS:
        if collection in project and not isinstance(project[collection], list):
            raise ValueError(f"Project '{collection}' must be a list")

    if not isinstance(project.get("metadata"), dict):
        raise ValueError("Project 'metadata' must be a dict")


def create_document(
    name: str = "Untitled",
    units: str = "mm",
    profile: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new project document.

    Parameters
    ----------
    name:
        Human-readable project name.
    units:
        Unit system (``"mm"``, ``"m"``, or ``"in"``).  Overridden by
        *profile* when a profile is supplied.
    profile:
        Optional profile key from :data:`PROFILES`.  When given, the
        profile's ``units`` value takes precedence over the *units*
        argument.

    Returns
    -------
    Dict[str, Any]
        A new project dictionary ready for use.

    Raises
    ------
    ValueError
        If *name* is empty, *units* is invalid, or *profile* is unknown.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Document name must be a non-empty string")

    if profile is not None:
        if profile not in PROFILES:
            raise ValueError(
                f"Unknown profile '{profile}'. Available profiles: {', '.join(sorted(PROFILES))}"
            )
        units = PROFILES[profile]["units"]

    if units not in VALID_UNITS:
        raise ValueError(
            f"Invalid units '{units}'. Must be one of: {', '.join(sorted(VALID_UNITS))}"
        )

    now = _now_iso()

    project: Dict[str, Any] = {
        "version": PROJECT_SCHEMA_VERSION,
        "name": name.strip(),
        "units": units,
        "parts": [],
        "sketches": [],
        "bodies": [],
        "materials": [],
        "assemblies": [],
        "meshes": [],
        "techdraw_pages": [],
        "draft_objects": [],
        "measurements": [],
        "surfaces": [],
        "fem_analyses": [],
        "cam_jobs": [],
        "spreadsheets": [],
        "motions": [],
        "metadata": {
            "created": now,
            "modified": now,
            "software": SOFTWARE_VERSION,
        },
    }
    return project
