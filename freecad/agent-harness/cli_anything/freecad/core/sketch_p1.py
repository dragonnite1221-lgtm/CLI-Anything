# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403


def _next_id(project: Dict[str, Any], collection_key: str = "sketches") -> int:
    """Generate the next unique ID for a collection."""
    items = project.get(collection_key, [])
    existing_ids = [item.get("id", 0) for item in items]
    return max(existing_ids, default=-1) + 1


def _unique_name(
    project: Dict[str, Any], base_name: str, collection_key: str = "sketches"
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


def _next_element_id(sketch: Dict[str, Any]) -> int:
    """Generate the next unique element ID within a sketch."""
    elements = sketch.get("elements", [])
    existing_ids = [el.get("id", 0) for el in elements]
    return max(existing_ids, default=-1) + 1


def _next_constraint_id(sketch: Dict[str, Any]) -> int:
    """Generate the next unique constraint ID within a sketch."""
    constraints = sketch.get("constraints", [])
    existing_ids = [c.get("id", 0) for c in constraints]
    return max(existing_ids, default=-1) + 1


def _validate_project(project: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if *project* is not a valid dict with a sketches list."""
    if not isinstance(project, dict):
        raise ValueError("Project must be a dictionary")
    if "sketches" not in project:
        raise ValueError("Project is missing 'sketches' collection")
    if not isinstance(project["sketches"], list):
        raise ValueError("Project 'sketches' must be a list")


def _get_sketch(project: Dict[str, Any], sketch_index: int) -> Dict[str, Any]:
    """Return sketch at *sketch_index* or raise ``IndexError``."""
    sketches = project["sketches"]
    if sketch_index < 0 or sketch_index >= len(sketches):
        raise IndexError(
            f"Sketch index {sketch_index} out of range (0-{len(sketches) - 1})"
        )
    return sketches[sketch_index]


def _validate_point_2d(point: List[float], label: str = "point") -> List[float]:
    """Validate and return a 2D point as a list of two floats."""
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ValueError(f"{label} must be a list of 2 numbers, got {point!r}")
    try:
        return [float(point[0]), float(point[1])]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} components must be numeric: {exc}") from exc


def create_sketch(
    project: Dict[str, Any],
    name: Optional[str] = None,
    plane: str = "XY",
    offset: float = 0.0,
) -> Dict[str, Any]:
    """Create a new sketch on the specified plane.

    Parameters
    ----------
    project:
        The project dictionary.
    name:
        Optional sketch name.  Auto-generated if ``None``.
    plane:
        Reference plane: ``"XY"``, ``"XZ"``, or ``"YZ"``.
    offset:
        Offset distance from the reference plane.

    Returns
    -------
    Dict[str, Any]
        The newly created sketch dictionary.

    Raises
    ------
    ValueError
        If the plane is invalid or the project is malformed.
    """
    _validate_project(project)

    plane = plane.upper()
    if plane not in VALID_PLANES:
        raise ValueError(
            f"Invalid plane '{plane}'. Must be one of: {', '.join(sorted(VALID_PLANES))}"
        )

    offset = float(offset)

    base_name = name if name else "Sketch"
    sketch_name = _unique_name(project, base_name)

    sketch: Dict[str, Any] = {
        "id": _next_id(project),
        "name": sketch_name,
        "plane": plane,
        "offset": offset,
        "elements": [],
        "constraints": [],
        "closed": False,
    }

    project["sketches"].append(sketch)
    return sketch
