# ruff: noqa: F403, F405, E402, F401, E501
from .preview_base import *
from .preview_p1 import _now_iso
from .preview_p2 import _write_live_session_updates

from . import preview_base as _coupbase  # noqa: E402


def record_live_poller_spawn(
    session_dir: str, *, pid: int, command: List[str], log_path: Optional[str] = None
) -> Dict[str, Any]:
    """Persist initial poller spawn metadata before the worker heartbeat lands."""
    session_path = Path(session_dir).expanduser().resolve()
    return _write_live_session_updates(
        session_path,
        {
            "poller": {
                "pid": int(pid),
                "running": True,
                "spawned_at": _coupbase._COUP_GLOBALS["_now_iso"](),
                "command": command,
                "log_path": log_path,
            }
        },
    )
