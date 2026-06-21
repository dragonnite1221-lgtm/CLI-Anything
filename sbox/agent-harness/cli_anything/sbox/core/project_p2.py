# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


def _default_sbproj(
    name: str,
    project_type: str = "game",
    org: str = "local",
    max_players: int = 64,
    tick_rate: int = 50,
    network_type: str = "Multiplayer",
    startup_scene: str = "scenes/minimal.scene",
) -> Dict[str, Any]:
    """Build a default .sbproj dict."""
    return {
        "Title": name,
        "Type": project_type,
        "Org": org,
        "Ident": name.lower().replace(" ", "_"),
        "Schema": 1,
        "HasAssets": True,
        "AssetsPath": "",
        "HasCode": True,
        "CodePath": "/code/",
        "Metadata": {
            "MaxPlayers": max_players,
            "MinPlayers": 1,
            "TickRate": tick_rate,
            "GameNetworkType": network_type,
            "MapSelect": "Tagged",
            "MapList": [],
            "RankType": "None",
            "PerMapRanking": False,
            "LeaderboardType": "None",
            "CsProjName": "",
            "StartupScene": startup_scene,
        },
        "PackageReferences": [],
        "EditorReferences": [],
        "IsWhitelistDisabled": False,
        "Physics": {
            "SubSteps": 1,
            "TimeScale": 1,
            "Gravity": "0,0,-800",
            "AirDensity": 1.2,
            "SleepingEnabled": True,
            "SimulationMode": "Continuous",
            "PositionIterations": 2,
            "VelocityIterations": 8,
        },
        "__references": [],
        "__version": 1,
    }
def _write_json(path: str, data: Dict[str, Any]) -> None:
    """Write data as formatted JSON to path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
def _write_text(path: str, content: str) -> None:
    """Write text content to path, ensuring parent dirs exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)
