# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403

# fmt: off
from .preview_p1 import _normalize_poll_ms  # noqa: E402,E501
from .preview_p2 import _load_existing_live_session  # noqa: E402,E501
from .preview_p8 import poll_live_session_once  # noqa: E402,E501
# fmt: on


def run_live_poller(session_dir: str) -> Dict[str, Any]:
    """Run the long-lived poll loop for a live session."""
    session_path = Path(session_dir).expanduser().resolve()
    while True:
        result = poll_live_session_once(str(session_path))
        if result.get("action") == "exit":
            return result
        payload = _load_existing_live_session(session_path)
        poll_ms = _normalize_poll_ms((payload or {}).get("source_poll_ms"))
        time.sleep(poll_ms / 1000.0)
