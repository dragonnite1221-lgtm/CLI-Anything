# ruff: noqa: F403, F405, E501
from .parts_base import *  # noqa: F403


def _next_id(project: Dict[str, Any], key: str = "parts") -> int:
    """Return the next available integer ID for *key* in *project*.

    Scans existing items under ``project[key]`` and returns one more than
    the current maximum ``id`` value, or ``1`` if the list is empty.
    """
    items = project.get(key, [])
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str, key: str = "parts") -> str:
    """Return a unique name derived from *base* inside ``project[key]``.

    If *base* is not yet taken the string is returned as-is; otherwise a
    numeric suffix is appended (e.g. ``Box_2``, ``Box_3``).
    """
    existing = {item["name"] for item in project.get(key, [])}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_vec3(value: Any, label: str) -> List[float]:
    """Validate that *value* is a list of exactly three numbers.

    Returns the value normalised to a list of Python floats.

    Raises ``ValueError`` with a descriptive message on failure.
    """
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"{label} must be a list of 3 numbers, got {type(value).__name__}"
        )
    if len(value) != 3:
        raise ValueError(f"{label} must have exactly 3 elements, got {len(value)}")
    try:
        return [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _rotation_matrix(rotation: List[float]) -> List[List[float]]:
    """Return a simple XYZ Euler rotation matrix for *rotation* in degrees."""
    rx, ry, rz = [math.radians(float(v)) for v in rotation]
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    mx = [
        [1.0, 0.0, 0.0],
        [0.0, cx, -sx],
        [0.0, sx, cx],
    ]
    my = [
        [cy, 0.0, sy],
        [0.0, 1.0, 0.0],
        [-sy, 0.0, cy],
    ]
    mz = [
        [cz, -sz, 0.0],
        [sz, cz, 0.0],
        [0.0, 0.0, 1.0],
    ]

    def _matmul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        return [
            [sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3)]
            for row in range(3)
        ]

    return _matmul(mz, _matmul(my, mx))


def _transform_point(
    point: List[float], rotation: List[float], translation: List[float]
) -> List[float]:
    """Apply an XYZ Euler rotation and translation to a point."""
    matrix = _rotation_matrix(rotation)
    x, y, z = point
    tx, ty, tz = translation
    return [
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z + tx,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z + ty,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z + tz,
    ]


def _bbox_from_points(points: List[List[float]]) -> Dict[str, Dict[str, float]]:
    """Build min/max/size/center dictionaries from transformed points."""
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]
    min_corner = {"x": min(xs), "y": min(ys), "z": min(zs)}
    max_corner = {"x": max(xs), "y": max(ys), "z": max(zs)}
    return {
        "min": min_corner,
        "max": max_corner,
        "size": {axis: max_corner[axis] - min_corner[axis] for axis in ("x", "y", "z")},
        "center": {
            axis: (min_corner[axis] + max_corner[axis]) / 2.0
            for axis in ("x", "y", "z")
        },
    }
