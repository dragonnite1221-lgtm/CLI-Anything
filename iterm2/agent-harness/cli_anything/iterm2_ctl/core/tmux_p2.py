# ruff: noqa: F403, F405, E501
from .tmux_base import *  # noqa: F403


async def list_tmux_tabs(connection) -> List[Dict[str, Any]]:
    """List all iTerm2 tabs that are backed by a tmux integration window.

    Returns only tabs that have a non-None tmux_window_id.
    """
    import iterm2

    app = await iterm2.async_get_app(connection)
    result = []
    for window in app.windows:
        for tab in window.tabs:
            if tab.tmux_window_id is not None:
                result.append(
                    {
                        "tab_id": tab.tab_id,
                        "window_id": window.window_id,
                        "tmux_window_id": tab.tmux_window_id,
                        "tmux_connection_id": tab.tmux_connection_id,
                        "session_count": len(tab.sessions),
                    }
                )
    return result


async def bootstrap(
    connection,
    attach: bool = False,
    session_id: Optional[str] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """Start a tmux -CC session in iTerm2 and wait for the connection to appear.

    Sends `tmux -CC` (or `tmux -CC attach`) to a session, then polls
    async_get_tmux_connections() until the connection materialises or the
    timeout expires.

    Args:
        attach: If True, send `tmux -CC attach` instead of `tmux -CC`.
        session_id: Which iTerm2 session to start tmux in. If None, uses the
            current window's first session.
        timeout: Seconds to wait for the connection to appear. Default 15.

    Returns:
        Dict with 'connection_id', 'owning_session_id', 'command', and
        'elapsed_seconds'.
    """
    import asyncio
    import iterm2
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    app = await iterm2.async_get_app(connection)

    # Resolve session
    if session_id is not None:
        target = await async_find_session(connection, session_id)
    else:
        # Fall back to first session in current window
        if not app.windows:
            raise RuntimeError("No iTerm2 windows open. Create one first.")
        target = app.windows[0].current_tab.current_session

    # Snapshot existing connections so we detect the new one
    existing_ids = {
        c.connection_id for c in await iterm2.async_get_tmux_connections(connection)
    }

    cmd = "tmux -CC attach" if attach else "tmux -CC"
    await target.async_send_text(cmd + "\n")

    # Poll until a new connection appears
    start = asyncio.get_event_loop().time()
    while True:
        await asyncio.sleep(0.5)
        current = await iterm2.async_get_tmux_connections(connection)
        new_conns = [c for c in current if c.connection_id not in existing_ids]
        if new_conns:
            nc = new_conns[0]
            owning = nc.owning_session
            elapsed = asyncio.get_event_loop().time() - start
            return {
                "connection_id": nc.connection_id,
                "owning_session_id": owning.session_id if owning else None,
                "command": cmd,
                "elapsed_seconds": round(elapsed, 2),
            }
        if asyncio.get_event_loop().time() - start > timeout:
            raise RuntimeError(
                f"Timed out after {timeout}s waiting for tmux -CC connection. "
                "Make sure tmux is installed and no existing session conflicts."
            )


async def run_session_tmux_command(
    connection,
    session_id: str,
    command: str,
) -> Dict[str, Any]:
    """Run a tmux command from within a specific session.

    The session must be a tmux integration session (i.e. the shell running
    inside it is connected to tmux -CC). Raises if the session is not tmux.

    Args:
        session_id: The iTerm2 session ID.
        command: A tmux command to run (e.g. "rename-window foo").
    """
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    output = await session.async_run_tmux_command(command)
    return {
        "session_id": session_id,
        "command": command,
        "output": output,
    }
