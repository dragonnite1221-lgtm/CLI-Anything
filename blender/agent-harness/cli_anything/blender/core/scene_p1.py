# ruff: noqa: F403, F405, E501
from .scene_base import *  # noqa: F403


def create_scene(
    name: str = "untitled",
    profile: Optional[str] = None,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    engine: str = "CYCLES",
    samples: int = 128,
    fps: int = 24,
    frame_start: int = 1,
    frame_end: int = 250,
) -> Dict[str, Any]:
    """Create a new Blender scene (JSON project)."""
    if profile and profile in PROFILES:
        p = PROFILES[profile]
        resolution_x = p["resolution_x"]
        resolution_y = p["resolution_y"]
        engine = p["engine"]
        samples = p["samples"]
        fps = p["fps"]

    if engine not in ("CYCLES", "EEVEE", "WORKBENCH"):
        raise ValueError(
            f"Invalid render engine: {engine}. Use CYCLES, EEVEE, or WORKBENCH."
        )
    if resolution_x < 1 or resolution_y < 1:
        raise ValueError(f"Resolution must be positive: {resolution_x}x{resolution_y}")
    if samples < 1:
        raise ValueError(f"Samples must be positive: {samples}")
    if fps < 1:
        raise ValueError(f"FPS must be positive: {fps}")
    if frame_start < 0:
        raise ValueError(f"Frame start must be non-negative: {frame_start}")
    if frame_end < frame_start:
        raise ValueError(
            f"Frame end ({frame_end}) must be >= frame start ({frame_start})"
        )

    project = {
        "version": PROJECT_VERSION,
        "name": name,
        "scene": {
            "unit_system": "metric",
            "unit_scale": 1.0,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "frame_current": frame_start,
            "fps": fps,
        },
        "render": {
            "engine": engine,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
            "resolution_percentage": 100,
            "samples": samples,
            "use_denoising": True,
            "film_transparent": False,
            "output_format": "PNG",
            "output_path": "./render/",
        },
        "world": {
            "background_color": [0.05, 0.05, 0.05],
            "use_hdri": False,
            "hdri_path": None,
            "hdri_strength": 1.0,
        },
        "objects": [],
        "materials": [],
        "cameras": [],
        "lights": [],
        "collections": [
            {"id": 0, "name": "Collection", "objects": [], "visible": True}
        ],
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "software": "blender-cli 1.0",
        },
    }
    return project


def open_scene(path: str) -> Dict[str, Any]:
    """Open a .blend-cli.json scene file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Scene file not found: {path}")
    with open(path, "r") as f:
        project = json.load(f)
    if "version" not in project or "scene" not in project:
        raise ValueError(f"Invalid scene file: {path}")
    return project


def save_scene(project: Dict[str, Any], path: str) -> str:
    """Save scene to a .blend-cli.json file."""
    project["metadata"]["modified"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(project, f, indent=2, default=str)
    return path
