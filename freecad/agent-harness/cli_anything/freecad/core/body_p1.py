# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403


def _next_id(project: Dict[str, Any], collection_key: str = "bodies") -> int:
    """Generate the next unique ID for a collection."""
    items = project.get(collection_key, [])
    existing_ids = [item.get("id", 0) for item in items]
    return max(existing_ids, default=-1) + 1


def _unique_name(
    project: Dict[str, Any], base_name: str, collection_key: str = "bodies"
) -> str:
    """Generate a unique name within a collection."""
    items = project.get(collection_key, [])
    existing_names = {item.get("name", "") for item in items}
    if base_name not in existing_names:
        return base_name
    counter = 1
    while f"{base_name}.{counter:03d}" in existing_names:
        counter += 1
    return f"{base_name}.{counter:03d}"


def _next_feature_id(body: Dict[str, Any]) -> int:
    """Generate the next unique feature ID within a body."""
    features = body.get("features", [])
    existing_ids = [f.get("id", 0) for f in features]
    return max(existing_ids, default=-1) + 1


def _validate_project(project: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if *project* is not a valid dict with required collections."""
    if not isinstance(project, dict):
        raise ValueError("Project must be a dictionary")
    if "bodies" not in project:
        raise ValueError("Project is missing 'bodies' collection")
    if not isinstance(project["bodies"], list):
        raise ValueError("Project 'bodies' must be a list")


def _get_body(project: Dict[str, Any], body_index: int) -> Dict[str, Any]:
    """Return body at *body_index* or raise ``IndexError``."""
    bodies = project["bodies"]
    if body_index < 0 or body_index >= len(bodies):
        raise IndexError(f"Body index {body_index} out of range (0-{len(bodies) - 1})")
    return bodies[body_index]


def _validate_sketch_index(
    project: Dict[str, Any], sketch_index: int
) -> Dict[str, Any]:
    """Validate that a sketch index exists and return the sketch."""
    sketches = project.get("sketches", [])
    if not isinstance(sketches, list):
        raise ValueError("Project 'sketches' must be a list")
    if sketch_index < 0 or sketch_index >= len(sketches):
        raise IndexError(
            f"Sketch index {sketch_index} out of range (0-{len(sketches) - 1})"
        )
    return sketches[sketch_index]


def _validate_vec3(value: Optional[List[float]], label: str) -> Optional[List[float]]:
    """Validate and normalize a 3-component vector."""
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label} must be a list of 3 numbers")
    return [float(component) for component in value]


def _normalize_feature_placement(
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Optional[Dict[str, List[float]]]:
    """Normalize optional position/rotation into a placement payload."""
    pos = _validate_vec3(position, "position")
    rot = _validate_vec3(rotation, "rotation")
    if pos is None and rot is None:
        return None
    return {
        "position": pos or [0.0, 0.0, 0.0],
        "rotation": rot or [0.0, 0.0, 0.0],
    }


def create_body(
    project: Dict[str, Any],
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new PartDesign body.

    Parameters
    ----------
    project:
        The project dictionary.
    name:
        Optional body name.  Auto-generated if ``None``.

    Returns
    -------
    Dict[str, Any]
        The newly created body dictionary.
    """
    _validate_project(project)

    base_name = name if name else "Body"
    body_name = _unique_name(project, base_name)

    body: Dict[str, Any] = {
        "id": _next_id(project),
        "name": body_name,
        "features": [],
        "base_sketch_index": None,
    }

    project["bodies"].append(body)
    return body
