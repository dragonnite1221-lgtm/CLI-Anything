# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403

# fmt: off
from .session_p2 import _get_process_name  # noqa: E402,E501
# fmt: on


async def workspace_snapshot(connection) -> Dict[str, Any]:
    """Rich snapshot of every session: name, path, pid, process, role, last screen line.

    For each session across all windows and tabs, returns:
      - session_id, name, window_id, tab_id
      - path:    current working directory (from iTerm2 session variable)
      - pid:     shell PID (from iTerm2 session variable)
      - process: foreground process name derived from pid via ps
      - role:    value of user.role session variable, or null if not set
      - last_line: last non-empty line currently visible on screen

    Use this instead of app status when you need to understand *what is
    happening* in each pane, not just that it exists.
    """
    import iterm2

    app = await iterm2.async_get_app(connection)
    sessions = []

    for window in app.windows:
        for tab in window.tabs:
            for session in tab.sessions:
                path = await session.async_get_variable("path")
                pid = await session.async_get_variable("pid")
                role = await session.async_get_variable("user.role")
                process = _get_process_name(pid)

                last_line = None
                contents = await session.async_get_screen_contents()
                for i in range(contents.number_of_lines - 1, -1, -1):
                    line = contents.line(i).string.strip()
                    if line:
                        last_line = line
                        break

                sessions.append(
                    {
                        "session_id": session.session_id,
                        "name": session.name,
                        "window_id": window.window_id,
                        "tab_id": tab.tab_id,
                        "path": path,
                        "pid": pid,
                        "process": process,
                        "role": role,
                        "last_line": last_line,
                    }
                )

    return {"session_count": len(sessions), "sessions": sessions}


async def set_grid_size(
    connection, session_id: str, columns: int, rows: int
) -> Dict[str, Any]:
    """Set the terminal grid size (columns x rows) for a session."""
    import iterm2
    from cli_anything.iterm2_ctl.utils.iterm2_backend import async_find_session

    session = await async_find_session(connection, session_id)
    size = iterm2.util.Size(width=columns, height=rows)
    await session.async_set_grid_size(size)
    return {"session_id": session_id, "columns": columns, "rows": rows}
