# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


def create_project(
    name: str = "untitled",
    profile: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    fps_num: int = 30,
    fps_den: int = 1,
    progressive: bool = True,
    dar_num: int = 16,
    dar_den: int = 9,
) -> Dict[str, Any]:
    """Create a new Kdenlive project (JSON format)."""
    if profile and profile in PROFILES:
        p = PROFILES[profile]
        width = p["width"]
        height = p["height"]
        fps_num = p["fps_num"]
        fps_den = p["fps_den"]
        progressive = p["progressive"]
        dar_num = p["dar_num"]
        dar_den = p["dar_den"]
    elif profile and profile not in PROFILES:
        raise ValueError(
            f"Unknown profile: {profile}. Available: {', '.join(PROFILES.keys())}"
        )

    if width < 1 or height < 1:
        raise ValueError(f"Resolution must be positive: {width}x{height}")
    if fps_num < 1 or fps_den < 1:
        raise ValueError(
            f"FPS numerator and denominator must be positive: {fps_num}/{fps_den}"
        )
    if dar_num < 1 or dar_den < 1:
        raise ValueError(f"Display aspect ratio must be positive: {dar_num}:{dar_den}")

    profile_name = profile if profile else "custom"

    project = {
        "version": PROJECT_VERSION,
        "name": name,
        "profile": {
            "name": profile_name,
            "width": width,
            "height": height,
            "fps_num": fps_num,
            "fps_den": fps_den,
            "progressive": progressive,
            "dar_num": dar_num,
            "dar_den": dar_den,
        },
        "bin": [],
        "tracks": [],
        "transitions": [],
        "guides": [],
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "software": "kdenlive-cli 1.0",
        },
    }
    return project


def open_project(path: str) -> Dict[str, Any]:
    """Open a .kdenlive-cli.json project file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")
    with open(path, "r") as f:
        project = json.load(f)
    if "version" not in project or "profile" not in project:
        raise ValueError(f"Invalid project file: {path}")
    return project


def save_project(project: Dict[str, Any], path: str) -> str:
    """Save project to a .kdenlive-cli.json file."""
    project["metadata"]["modified"] = datetime.now().isoformat()
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w") as f:
        json.dump(project, f, indent=2, default=str)
    return path
