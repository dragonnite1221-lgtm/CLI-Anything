# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


async def get_scrollback(
    connection,
    session_id: str,
    lines: Optional[int] = None,
    tail: Optional[int] = None,
) -> Dict[str, Any]:
    """Get the full scrollback buffer including history beyond the visible screen.

    Uses async_get_line_info() + async_get_contents() inside a Transaction for
    consistency. This reads ALL available lines — scrollback history + visible
    screen — not just what's currently visible.

    Args:
        session_id: Target session.
        lines: Max total lines to return (None = all available). Applied from
            the oldest line forward.
        tail: If set, return only the last N lines (most recent). Takes
            precedence over `lines`.

    Returns:
        Dict with:
          - lines: list of line strings (oldest → newest)
          - total_available: scrollback_buffer_height + mutable_area_height
          - scrollback_lines: lines in the history buffer
          - screen_lines: lines in the visible mutable area
          - overflow: lines lost due to buffer overflow
          - returned_lines: count actually returned
    """
    import iterm2
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)

    async with iterm2.Transaction(connection):
        li = await session.async_get_line_info()
        total_available = li.scrollback_buffer_height + li.mutable_area_height

        if tail is not None:
            # Read only the last `tail` lines
            want = min(tail, total_available)
            first_line = li.overflow + (total_available - want)
            count = want
        elif lines is not None:
            first_line = li.overflow
            count = min(lines, total_available)
        else:
            first_line = li.overflow
            count = total_available

        raw = await session.async_get_contents(first_line, count)

    result_lines = [lc.string for lc in raw]
    return {
        "session_id": session_id,
        "total_available": total_available,
        "scrollback_lines": li.scrollback_buffer_height,
        "screen_lines": li.mutable_area_height,
        "overflow": li.overflow,
        "returned_lines": len(result_lines),
        "lines": result_lines,
    }


async def get_selection(connection, session_id: str) -> Dict[str, Any]:
    """Get the currently selected text in a session."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    selection_text = await session.async_get_selection_text(
        await session.async_get_selection()
    )
    return {
        "session_id": session_id,
        "selected_text": selection_text,
        "has_selection": bool(selection_text),
    }


async def set_session_name(connection, session_id: str, name: str) -> Dict[str, Any]:
    """Set the name of a session (shown in the tab bar)."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_set_name(name)
    return {"session_id": session_id, "name": name}


async def restart_session(
    connection, session_id: str, only_if_exited: bool = False
) -> Dict[str, Any]:
    """Restart a session."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_restart(only_if_exited=only_if_exited)
    return {"session_id": session_id, "restarted": True}


async def get_session_variable(
    connection, session_id: str, variable_name: str
) -> Dict[str, Any]:
    """Get a session variable value."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    value = await session.async_get_variable(variable_name)
    return {
        "session_id": session_id,
        "variable": variable_name,
        "value": value,
    }


async def set_session_variable(
    connection, session_id: str, variable_name: str, value: Any
) -> Dict[str, Any]:
    """Set a session variable."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_set_variable(variable_name, value)
    return {
        "session_id": session_id,
        "variable": variable_name,
        "value": value,
        "set": True,
    }


async def inject_bytes(connection, session_id: str, data: bytes) -> Dict[str, Any]:
    """Inject raw bytes into a session's input stream (as if received from the shell)."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    await session.async_inject(data)
    return {"session_id": session_id, "injected_bytes": len(data)}


def _get_process_name(pid) -> Optional[str]:
    """Return the process name for a given PID using ps, or None on failure."""
    import subprocess

    if pid is None:
        return None
    try:
        result = subprocess.run(
            ["ps", "-p", str(int(pid)), "-o", "comm="],
            capture_output=True,
            text=True,
            timeout=2,
        )
        name = result.stdout.strip()
        return name.split("/")[-1] if name else None
    except Exception:
        return None
