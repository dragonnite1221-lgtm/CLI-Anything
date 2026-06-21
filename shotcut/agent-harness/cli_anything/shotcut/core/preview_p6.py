# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p3 import _now_iso, _write_live_session_updates  # noqa: E402,E501
# fmt: on


def record_live_poller_spawn(
    session_dir: str,
    *,
    pid: int,
    command: List[str],
    log_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist initial poller spawn metadata before the worker heartbeat lands."""
    session_path = Path(session_dir).expanduser().resolve()
    return _write_live_session_updates(
        session_path,
        {
            "poller": {
                "pid": int(pid),
                "running": True,
                "spawned_at": _now_iso(),
                "command": command,
                "log_path": log_path,
            }
        },
    )
