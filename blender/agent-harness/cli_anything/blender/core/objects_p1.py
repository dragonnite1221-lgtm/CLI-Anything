# ruff: noqa: F403, F405, E501
from .objects_base import *  # noqa: F403


def _next_id(project: Dict[str, Any], collection_key: str = "objects") -> int:
    """Generate the next unique ID for a collection."""
    items = project.get(collection_key, [])
    existing_ids = [item.get("id", 0) for item in items]
    return max(existing_ids, default=-1) + 1


def _unique_name(
    project: Dict[str, Any], base_name: str, collection_key: str = "objects"
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


def add_object(
    project: Dict[str, Any],
    mesh_type: str = "cube",
    name: Optional[str] = None,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
    mesh_params: Optional[Dict[str, Any]] = None,
    collection: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a 3D primitive object to the scene.

    Args:
        project: The scene dict
        mesh_type: Primitive type (cube, sphere, cylinder, cone, plane, torus, monkey, empty)
        name: Object name (auto-generated if None)
        location: [x, y, z] location (default [0, 0, 0])
        rotation: [x, y, z] rotation in degrees (default [0, 0, 0])
        scale: [x, y, z] scale (default [1, 1, 1])
        mesh_params: Override mesh creation parameters
        collection: Target collection name (default: first collection)

    Returns:
        The new object dict
    """
    if mesh_type not in MESH_PRIMITIVES:
        raise ValueError(
            f"Unknown mesh type: {mesh_type}. Valid types: {list(MESH_PRIMITIVES.keys())}"
        )

    if location is not None and len(location) != 3:
        raise ValueError(
            f"Location must have 3 components [x, y, z], got {len(location)}"
        )
    if rotation is not None and len(rotation) != 3:
        raise ValueError(
            f"Rotation must have 3 components [x, y, z], got {len(rotation)}"
        )
    if scale is not None and len(scale) != 3:
        raise ValueError(f"Scale must have 3 components [x, y, z], got {len(scale)}")

    # Merge default params with overrides
    default_params = dict(MESH_PRIMITIVES[mesh_type])
    if mesh_params:
        for k, v in mesh_params.items():
            if k not in default_params and mesh_type != "empty":
                valid_keys = list(MESH_PRIMITIVES[mesh_type].keys())
                raise ValueError(
                    f"Unknown mesh param '{k}' for {mesh_type}. Valid: {valid_keys}"
                )
            default_params[k] = v

    base_name = name or mesh_type.capitalize()
    obj_name = _unique_name(project, base_name, "objects")
    obj_type = "EMPTY" if mesh_type == "empty" else "MESH"

    obj = {
        "id": _next_id(project, "objects"),
        "name": obj_name,
        "type": obj_type,
        "mesh_type": mesh_type,
        "location": list(location) if location else [0.0, 0.0, 0.0],
        "rotation": list(rotation) if rotation else [0.0, 0.0, 0.0],
        "scale": list(scale) if scale else [1.0, 1.0, 1.0],
        "visible": True,
        "material": None,
        "modifiers": [],
        "keyframes": [],
        "parent": None,
        "mesh_params": default_params,
    }

    if "objects" not in project:
        project["objects"] = []
    project["objects"].append(obj)

    # Add to collection
    if collection:
        collections = project.get("collections", [])
        target = None
        for c in collections:
            if c["name"] == collection:
                target = c
                break
        if target is None:
            raise ValueError(f"Collection not found: {collection}")
        target["objects"].append(obj["id"])
    else:
        # Add to first collection if it exists
        collections = project.get("collections", [])
        if collections:
            collections[0]["objects"].append(obj["id"])

    return obj


def remove_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove an object by index."""
    objects = project.get("objects", [])
    if not objects:
        raise ValueError("No objects to remove")
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    removed = objects.pop(index)

    # Remove from collections
    obj_id = removed.get("id")
    for c in project.get("collections", []):
        if obj_id in c.get("objects", []):
            c["objects"].remove(obj_id)

    # Remove material references that point to this object
    # (materials stand alone, we just clear the object's reference)

    return removed


def duplicate_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Duplicate an object."""
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    original = objects[index]
    dup = copy.deepcopy(original)
    dup["id"] = _next_id(project, "objects")
    dup["name"] = _unique_name(project, f"{original['name']}.copy", "objects")
    objects.append(dup)

    # Add to same collections as original
    orig_id = original.get("id")
    for c in project.get("collections", []):
        if orig_id in c.get("objects", []):
            c["objects"].append(dup["id"])

    return dup
