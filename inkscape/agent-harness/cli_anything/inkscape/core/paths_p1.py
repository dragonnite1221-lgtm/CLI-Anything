# ruff: noqa: F403, F405, E501
from .paths_base import *  # noqa: F403


def _path_boolean(
    project: Dict[str, Any],
    index_a: int,
    index_b: int,
    operation: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Perform a boolean path operation between two objects."""
    objects = project.get("objects", [])
    if index_a < 0 or index_a >= len(objects):
        raise IndexError(
            f"Object A index {index_a} out of range (0-{len(objects) - 1})"
        )
    if index_b < 0 or index_b >= len(objects):
        raise IndexError(
            f"Object B index {index_b} out of range (0-{len(objects) - 1})"
        )
    if index_a == index_b:
        raise ValueError("Cannot perform boolean operation on the same object")

    obj_a = objects[index_a]
    obj_b = objects[index_b]

    # Create a new path object representing the boolean result
    obj_id = generate_id("path")
    result_obj = {
        "id": obj_id,
        "name": name or f"{operation}_{obj_a.get('name', '')}_{obj_b.get('name', '')}",
        "type": "path",
        "d": obj_a.get("d", "M 0,0"),  # Placeholder
        "style": obj_a.get("style", ""),
        "transform": "",
        "layer": obj_a.get("layer", ""),
        "boolean_operation": {
            "type": operation,
            "source_a": obj_a.get("id", ""),
            "source_b": obj_b.get("id", ""),
            "inkscape_action": PATH_OPERATIONS[operation]["inkscape_action"],
        },
    }

    # Remove the source objects (boolean ops consume both)
    # Remove higher index first to avoid index shifting
    higher = max(index_a, index_b)
    lower = min(index_a, index_b)

    removed_ids = {objects[higher].get("id", ""), objects[lower].get("id", "")}
    objects.pop(higher)
    objects.pop(lower)

    # Remove from layers
    for layer in project.get("layers", []):
        layer["objects"] = [
            oid for oid in layer.get("objects", []) if oid not in removed_ids
        ]

    # Add result object
    objects.append(result_obj)

    # Add to layer
    layer_id = result_obj.get("layer", "")
    for layer in project.get("layers", []):
        if layer.get("id") == layer_id:
            layer.setdefault("objects", []).append(obj_id)
            break

    return result_obj


def path_union(
    project: Dict[str, Any],
    index_a: int,
    index_b: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a union of two objects (stores as path operation record)."""
    return _path_boolean(project, index_a, index_b, "union", name)


def path_intersection(
    project: Dict[str, Any],
    index_a: int,
    index_b: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an intersection of two objects."""
    return _path_boolean(project, index_a, index_b, "intersection", name)


def path_difference(
    project: Dict[str, Any],
    index_a: int,
    index_b: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a difference of two objects (A minus B)."""
    return _path_boolean(project, index_a, index_b, "difference", name)


def path_exclusion(
    project: Dict[str, Any],
    index_a: int,
    index_b: int,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an exclusion (XOR) of two objects."""
    return _path_boolean(project, index_a, index_b, "exclusion", name)
