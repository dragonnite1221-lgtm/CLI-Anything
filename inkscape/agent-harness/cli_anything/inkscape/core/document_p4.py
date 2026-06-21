# ruff: noqa: F403, F405, E501
from .document_base import *  # noqa: F403


def get_document_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary information about the document."""
    doc = project.get("document", {})
    objects = project.get("objects", [])
    layers = project.get("layers", [])
    gradients = project.get("gradients", [])

    # Count objects by type
    type_counts = {}
    for obj in objects:
        t = obj.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "name": project.get("name", "untitled"),
        "version": project.get("version", "unknown"),
        "document": {
            "width": doc.get("width", 0),
            "height": doc.get("height", 0),
            "units": doc.get("units", "px"),
            "viewBox": doc.get("viewBox", ""),
            "background": doc.get("background", "#ffffff"),
        },
        "counts": {
            "objects": len(objects),
            "layers": len(layers),
            "gradients": len(gradients),
        },
        "object_types": type_counts,
        "objects": [
            {
                "id": o.get("id", ""),
                "name": o.get("name", ""),
                "type": o.get("type", "unknown"),
            }
            for o in objects
        ],
        "layers": [
            {
                "id": l.get("id", ""),
                "name": l.get("name", ""),
                "visible": l.get("visible", True),
                "locked": l.get("locked", False),
                "object_count": len(l.get("objects", [])),
            }
            for l in layers
        ],
        "metadata": project.get("metadata", {}),
    }


def set_canvas_size(
    project: Dict[str, Any], width: float, height: float
) -> Dict[str, Any]:
    """Set the canvas dimensions."""
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensions must be positive: {width}x{height}")
    old_w = project["document"]["width"]
    old_h = project["document"]["height"]
    project["document"]["width"] = width
    project["document"]["height"] = height
    project["document"]["viewBox"] = f"0 0 {width} {height}"
    return {
        "old_size": f"{old_w}x{old_h}",
        "new_size": f"{width}x{height}",
    }


def set_units(project: Dict[str, Any], units: str) -> Dict[str, Any]:
    """Set the document units."""
    if units not in VALID_UNITS:
        raise ValueError(
            f"Invalid units: {units}. Use one of: {', '.join(VALID_UNITS)}"
        )
    old = project["document"]["units"]
    project["document"]["units"] = units
    return {"old_units": old, "new_units": units}


def list_profiles() -> List[Dict[str, Any]]:
    """List all available document profiles."""
    result = []
    for name, p in PROFILES.items():
        result.append(
            {
                "name": name,
                "dimensions": f"{p['width']}x{p['height']}",
                "units": p["units"],
            }
        )
    return result
