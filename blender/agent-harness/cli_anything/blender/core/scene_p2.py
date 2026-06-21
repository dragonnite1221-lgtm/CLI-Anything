# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403


def get_scene_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary information about the scene."""
    scene = project.get("scene", {})
    render = project.get("render", {})
    objects = project.get("objects", [])
    materials = project.get("materials", [])
    cameras = project.get("cameras", [])
    lights = project.get("lights", [])
    return {
        "name": project.get("name", "untitled"),
        "version": project.get("version", "unknown"),
        "scene": {
            "unit_system": scene.get("unit_system", "metric"),
            "frame_range": f"{scene.get('frame_start', 1)}-{scene.get('frame_end', 250)}",
            "fps": scene.get("fps", 24),
            "current_frame": scene.get("frame_current", 1),
        },
        "render": {
            "engine": render.get("engine", "CYCLES"),
            "resolution": f"{render.get('resolution_x', 1920)}x{render.get('resolution_y', 1080)}",
            "samples": render.get("samples", 128),
            "output_format": render.get("output_format", "PNG"),
        },
        "counts": {
            "objects": len(objects),
            "materials": len(materials),
            "cameras": len(cameras),
            "lights": len(lights),
        },
        "objects": [
            {
                "id": o.get("id", i),
                "name": o.get("name", f"Object {i}"),
                "type": o.get("type", "MESH"),
                "mesh_type": o.get("mesh_type", "unknown"),
                "visible": o.get("visible", True),
            }
            for i, o in enumerate(objects)
        ],
        "metadata": project.get("metadata", {}),
    }


def list_profiles() -> List[Dict[str, Any]]:
    """List all available scene profiles."""
    result = []
    for name, p in PROFILES.items():
        result.append(
            {
                "name": name,
                "resolution": f"{p['resolution_x']}x{p['resolution_y']}",
                "engine": p["engine"],
                "samples": p["samples"],
                "fps": p["fps"],
            }
        )
    return result
