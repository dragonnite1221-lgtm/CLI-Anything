# ruff: noqa: F403, F405, E402, F401, E501
from .tmux_base import *

from . import tmux_base as _coupbase  # noqa: E402


async def _ensure_app_and_connections(connection):
    """Initialize App (sets up DELEGATE_FACTORY) then return tmux connections."""
    import iterm2

    await iterm2.async_get_app(connection)
    return await iterm2.async_get_tmux_connections(connection)


async def _resolve_connection(connection, connection_id: Optional[str]):
    """Return a TmuxConnection by ID, or the first one if ID is None."""
    connections = await _coupbase._COUP_GLOBALS["_ensure_app_and_connections"](
        connection
    )
    if not connections:
        raise RuntimeError(
            "No active tmux connections. Start one with:\n  tmux -CC        # in an iTerm2 terminal\n  tmux -CC attach # to attach to an existing session"
        )
    if connection_id is None:
        return connections[0]
    for c in connections:
        if c.connection_id == connection_id:
            return c
    available = [c.connection_id for c in connections]
    raise ValueError(
        f"Tmux connection '{connection_id}' not found. Available: {available}"
    )


async def list_connections(connection) -> List[Dict[str, Any]]:
    """List all active iTerm2 tmux integration connections.

    Each connection corresponds to a running `tmux -CC` session. Returns
    an empty list if no tmux integration is active.
    """
    connections = await _coupbase._COUP_GLOBALS["_ensure_app_and_connections"](
        connection
    )
    result = []
    for c in connections:
        owning = c.owning_session
        result.append(
            {
                "connection_id": c.connection_id,
                "owning_session_id": owning.session_id if owning else None,
                "owning_session_name": owning.name if owning else None,
            }
        )
    return result


async def send_command(
    connection, command: str, connection_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send a tmux command to an active tmux integration connection.

    Args:
        command: Any valid tmux command, e.g. "list-sessions", "new-window -n work".
        connection_id: Which connection to use (None = first available).

    Returns:
        Dict with the tmux command output.
    """
    tc = await _coupbase._COUP_GLOBALS["_resolve_connection"](connection, connection_id)
    output = await tc.async_send_command(command)
    return {"connection_id": tc.connection_id, "command": command, "output": output}


async def create_window(
    connection, connection_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new tmux window via iTerm2's integration.

    The new tmux window surfaces as a new iTerm2 tab. Returns window and
    tab info.

    Args:
        connection_id: Which tmux connection to use (None = first available).
    """
    tc = await _coupbase._COUP_GLOBALS["_resolve_connection"](connection, connection_id)
    window = await tc.async_create_window()
    if window is None:
        raise RuntimeError("Failed to create tmux window — got None from iTerm2")
    tab = window.current_tab
    session = tab.current_session if tab else None
    return {
        "connection_id": tc.connection_id,
        "window_id": window.window_id,
        "tab_id": tab.tab_id if tab else None,
        "session_id": session.session_id if session else None,
    }


async def set_window_visible(
    connection, tmux_window_id: str, visible: bool, connection_id: Optional[str] = None
) -> Dict[str, Any]:
    """Show or hide a tmux window (represented as an iTerm2 tab).

    Args:
        tmux_window_id: The tmux window ID (from tab.tmux_window_id, e.g. "@1").
        visible: True to show, False to hide.
        connection_id: Which tmux connection (None = first available).
    """
    tc = await _coupbase._COUP_GLOBALS["_resolve_connection"](connection, connection_id)
    await tc.async_set_tmux_window_visible(tmux_window_id, visible)
    return {
        "connection_id": tc.connection_id,
        "tmux_window_id": tmux_window_id,
        "visible": visible,
    }
