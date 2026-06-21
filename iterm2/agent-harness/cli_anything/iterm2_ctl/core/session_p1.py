# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


async def list_sessions(
    connection,
    window_id: Optional[str] = None,
    tab_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List all sessions, optionally filtered by window or tab."""
    import iterm2

    app = await iterm2.async_get_app(connection)
    result = []

    for window in app.windows:
        if window_id and window.window_id != window_id:
            continue
        for tab in window.tabs:
            if tab_id and tab.tab_id != tab_id:
                continue
            current_session = tab.current_session
            for session in tab.sessions:
                result.append(
                    {
                        "session_id": session.session_id,
                        "name": session.name,
                        "tab_id": tab.tab_id,
                        "window_id": window.window_id,
                        "is_current": (
                            current_session is not None
                            and session.session_id == current_session.session_id
                        ),
                    }
                )
    return result


async def get_session_info(connection, session_id: str) -> Dict[str, Any]:
    """Get info about a specific session."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    return {
        "session_id": session.session_id,
        "name": session.name,
    }


async def send_text(
    connection,
    session_id: str,
    text: str,
    suppress_broadcast: bool = False,
) -> Dict[str, Any]:
    """Send text/keystrokes to a session.

    Args:
        session_id: Target session ID.
        text: Text to send (use \\n for Enter).
        suppress_broadcast: If True, suppress sending to broadcast domains.

    Returns:
        Dict confirming the send.
    """
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_send_text(text, suppress_broadcast=suppress_broadcast)
    return {
        "session_id": session_id,
        "text_length": len(text),
        "sent": True,
    }


async def split_pane(
    connection,
    session_id: str,
    vertical: bool = False,
    before: bool = False,
    profile: Optional[str] = None,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    """Split a session into two panes.

    Args:
        session_id: Session to split.
        vertical: If True, split vertically (side by side). Default: horizontal (top/bottom).
        before: If True, new pane appears before the split point.
        profile: Profile name for new pane (None = same profile).
        command: Command to run in new pane (None = shell).

    Returns:
        Dict with new session_id.
    """
    import iterm2
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)

    profile_customizations = None
    if command:
        customizations = iterm2.LocalWriteOnlyProfile()
        customizations.set_use_custom_command("Yes")
        customizations.set_command(command)
        profile_customizations = customizations

    new_session = await session.async_split_pane(
        vertical=vertical,
        before=before,
        profile=profile,
        profile_customizations=profile_customizations,
    )
    if new_session is None:
        raise RuntimeError("Failed to split pane")
    return {
        "original_session_id": session_id,
        "new_session_id": new_session.session_id,
        "vertical": vertical,
    }


async def close_session(
    connection, session_id: str, force: bool = False
) -> Dict[str, Any]:
    """Close a session."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_close(force=force)
    return {"session_id": session_id, "closed": True}


async def activate_session(connection, session_id: str) -> Dict[str, Any]:
    """Bring a session to focus."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_activate()
    return {"session_id": session_id, "activated": True}


async def get_screen_contents(
    connection, session_id: str, lines: Optional[int] = None
) -> Dict[str, Any]:
    """Get the visible screen contents of a session.

    Args:
        session_id: Target session.
        lines: Number of lines to return (None = all visible lines).

    Returns:
        Dict with 'lines' list and metadata.
    """
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    contents = await session.async_get_screen_contents()
    total = contents.number_of_lines
    limit = lines if lines is not None else total
    screen_lines = []
    for i in range(min(limit, total)):
        line = contents.line(i)
        screen_lines.append(line.string)
    return {
        "session_id": session_id,
        "total_lines": total,
        "returned_lines": len(screen_lines),
        "lines": screen_lines,
    }
