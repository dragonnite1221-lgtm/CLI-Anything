# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403


def list_transitions(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all transitions."""
    return [
        {
            "id": t["id"],
            "type": t["type"],
            "mlt_service": t.get("mlt_service", ""),
            "track_a": t["track_a"],
            "track_b": t["track_b"],
            "position": t.get("position", 0),
            "duration": t.get("duration", 1),
            "params": t.get("params", {}),
        }
        for t in project.get("transitions", [])
    ]
