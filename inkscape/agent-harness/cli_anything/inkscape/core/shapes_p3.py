# ruff: noqa: F403, F405, E501
from .shapes_base import *  # noqa: F403


def duplicate_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Duplicate an object by index."""
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    original = objects[index]
    dup = copy.deepcopy(original)
    new_id = generate_id(dup.get("type", "obj"))
    dup["id"] = new_id
    dup["name"] = f"{original.get('name', 'object')}_copy"

    objects.append(dup)

    # Add to same layer
    layer_id = dup.get("layer", "")
    for layer in project.get("layers", []):
        if layer.get("id") == layer_id:
            layer["objects"].append(new_id)
            break

    return dup


def list_objects(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all objects in the document."""
    result = []
    for i, obj in enumerate(project.get("objects", [])):
        result.append(
            {
                "index": i,
                "id": obj.get("id", ""),
                "name": obj.get("name", ""),
                "type": obj.get("type", "unknown"),
                "layer": obj.get("layer", ""),
            }
        )
    return result


def get_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get detailed info about an object by index."""
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")
    return copy.deepcopy(objects[index])
