# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403
# fmt: off
from .project_p1 import CODE_ASSEMBLY_CS, DEFAULT_COLLISION_CONFIG, DEFAULT_INPUT_CONFIG, EDITORCONFIG_CONTENT, EDITOR_ASSEMBLY_CS, _default_minimal_scene  # noqa: E402,E501
from .project_p2 import _default_sbproj, _write_json, _write_text  # noqa: E402,E501
# fmt: on


def create_project(
    name: str,
    project_type: str = "game",
    org: str = "local",
    max_players: int = 64,
    tick_rate: int = 50,
    network_type: str = "Multiplayer",
    startup_scene: str = "scenes/minimal.scene",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new s&box project directory with .sbproj and standard structure.

    Creates:
    - <name>.sbproj
    - .editorconfig
    - Code/Assembly.cs
    - Editor/Assembly.cs
    - Assets/scenes/minimal.scene (basic scene)
    - ProjectSettings/Input.config (default bindings)
    - ProjectSettings/Collision.config (default layers)
    - Libraries/ (empty)
    - Localization/ (empty)

    Returns dict with project info.
    """
    root = output_dir if output_dir else os.path.join(os.getcwd(), name)
    os.makedirs(root, exist_ok=True)

    # .sbproj
    sbproj_data = _default_sbproj(
        name,
        project_type=project_type,
        org=org,
        max_players=max_players,
        tick_rate=tick_rate,
        network_type=network_type,
        startup_scene=startup_scene,
    )
    sbproj_path = os.path.join(root, f"{name}.sbproj")
    _write_json(sbproj_path, sbproj_data)

    # .editorconfig
    _write_text(os.path.join(root, ".editorconfig"), EDITORCONFIG_CONTENT)

    # Code/Assembly.cs
    code_dir = os.path.join(root, "Code")
    os.makedirs(code_dir, exist_ok=True)
    _write_text(os.path.join(code_dir, "Assembly.cs"), CODE_ASSEMBLY_CS)

    # Editor/Assembly.cs
    editor_dir = os.path.join(root, "Editor")
    os.makedirs(editor_dir, exist_ok=True)
    _write_text(os.path.join(editor_dir, "Assembly.cs"), EDITOR_ASSEMBLY_CS)

    # Assets/scenes/minimal.scene
    scenes_dir = os.path.join(root, "Assets", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)
    scene_data = _default_minimal_scene()
    _write_json(os.path.join(scenes_dir, "minimal.scene"), scene_data)

    # ProjectSettings
    settings_dir = os.path.join(root, "ProjectSettings")
    os.makedirs(settings_dir, exist_ok=True)
    _write_json(os.path.join(settings_dir, "Input.config"), DEFAULT_INPUT_CONFIG)
    _write_json(os.path.join(settings_dir, "Collision.config"), DEFAULT_COLLISION_CONFIG)

    # Empty directories
    os.makedirs(os.path.join(root, "Libraries"), exist_ok=True)
    os.makedirs(os.path.join(root, "Localization"), exist_ok=True)

    return {
        "name": name,
        "path": root,
        "sbproj": sbproj_path,
        "type": project_type,
        "org": org,
        "max_players": max_players,
        "tick_rate": tick_rate,
        "network_type": network_type,
        "startup_scene": startup_scene,
    }
def load_project(sbproj_path: str) -> Dict[str, Any]:
    """Load and return parsed .sbproj JSON."""
    with open(sbproj_path, "r", encoding="utf-8") as f:
        return json.load(f)
def save_project(sbproj_path: str, data: Dict[str, Any]) -> None:
    """Save .sbproj JSON."""
    _write_json(sbproj_path, data)
def get_project_info(sbproj_path: str) -> Dict[str, Any]:
    """Return dict with project metadata suitable for display/JSON output."""
    data = load_project(sbproj_path)
    meta = data.get("Metadata", {})
    return {
        "title": data.get("Title", ""),
        "type": data.get("Type", ""),
        "org": data.get("Org", ""),
        "ident": data.get("Ident", ""),
        "startup_scene": meta.get("StartupScene", ""),
        "max_players": meta.get("MaxPlayers"),
        "min_players": meta.get("MinPlayers"),
        "tick_rate": meta.get("TickRate"),
        "network_type": meta.get("GameNetworkType", ""),
        "map_select": meta.get("MapSelect", ""),
        "map_list": meta.get("MapList", []),
        "package_references": data.get("PackageReferences", []),
        "path": sbproj_path,
    }
