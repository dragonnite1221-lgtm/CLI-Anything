# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


def _empty_session_data() -> Dict[str, Any]:
    """Return a blank session data structure."""
    now = time.time()
    return {
        "project_path": None,
        "scene_path": None,
        "modified": False,
        "undo_stack": [],
        "redo_stack": [],
        "created_at": now,
        "updated_at": now,
    }
