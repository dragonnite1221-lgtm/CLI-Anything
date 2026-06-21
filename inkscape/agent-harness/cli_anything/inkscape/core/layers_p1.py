# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403


def add_layer(
    project: Dict[str, Any],
    name: str = "New Layer",
    visible: bool = True,
    locked: bool = False,
    opacity: float = 1.0,
    position: Optional[int] = None,
) -> Dict[str, Any]:
    """Add a new layer to the document.

    Args:
        position: Stack position (0 = bottom). None = top.
    """
    if opacity < 0 or opacity > 1:
        raise ValueError(f"Opacity must be 0.0-1.0: {opacity}")

    # Ensure unique name
    existing_names = {l.get("name", "") for l in project.get("layers", [])}
    final_name = name
    counter = 1
    while final_name in existing_names:
        counter += 1
        final_name = f"{name} {counter}"

    layer_id = generate_id("layer")
    layer = {
        "id": layer_id,
        "name": final_name,
        "visible": visible,
        "locked": locked,
        "opacity": opacity,
        "objects": [],
    }

    layers = project.setdefault("layers", [])
    if position is not None:
        position = max(0, min(position, len(layers)))
        layers.insert(position, layer)
    else:
        layers.append(layer)

    return layer


def remove_layer(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove a layer by index.

    Objects in the removed layer are moved to the first remaining layer,
    or orphaned if no layers remain.
    """
    layers = project.get("layers", [])
    if not layers:
        raise ValueError("No layers in document")
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")
    if len(layers) <= 1:
        raise ValueError("Cannot remove the last layer")

    removed = layers.pop(index)

    # Move orphaned objects to the first remaining layer
    orphaned_ids = removed.get("objects", [])
    if orphaned_ids and layers:
        target = layers[0]
        target.setdefault("objects", []).extend(orphaned_ids)
        # Update object layer references
        for obj in project.get("objects", []):
            if obj.get("id") in orphaned_ids:
                obj["layer"] = target["id"]

    return removed


def move_to_layer(
    project: Dict[str, Any],
    object_index: int,
    layer_index: int,
) -> Dict[str, Any]:
    """Move an object from its current layer to another layer."""
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    layers = project.get("layers", [])
    if layer_index < 0 or layer_index >= len(layers):
        raise IndexError(
            f"Layer index {layer_index} out of range (0-{len(layers) - 1})"
        )

    obj = objects[object_index]
    obj_id = obj.get("id", "")
    target_layer = layers[layer_index]

    # Remove from current layer
    for layer in layers:
        if obj_id in layer.get("objects", []):
            layer["objects"].remove(obj_id)

    # Add to target layer
    target_layer.setdefault("objects", []).append(obj_id)
    obj["layer"] = target_layer["id"]

    return {
        "object": obj.get("name", obj_id),
        "target_layer": target_layer.get("name", target_layer.get("id", "")),
    }
