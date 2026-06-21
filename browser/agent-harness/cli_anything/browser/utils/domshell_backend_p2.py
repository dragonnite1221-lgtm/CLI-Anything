# ruff: noqa: F403, F405, E501
from .domshell_backend_base import *  # noqa: F403

# fmt: off
from .domshell_backend_p1 import _build_server_args, _daemon_client_context, _daemon_read, _daemon_session, _daemon_write, _stop_daemon  # noqa: E402,E501
# fmt: on


async def _call_tool(tool_name: str, arguments: dict, use_daemon: bool = False) -> Any:
    """Call a DOMShell MCP tool.

    Args:
        tool_name: Name of the MCP tool (e.g., "domshell_ls", "domshell_cd")
        arguments: Arguments to pass to the tool
        use_daemon: If True, use persistent daemon connection (if available)

    Returns:
        Tool result as returned by MCP server

    Raises:
        RuntimeError: If MCP server is not available or tool call fails
    """
    global _daemon_session, _daemon_read, _daemon_write

    if use_daemon and _daemon_session is not None:
        # Use persistent daemon connection
        try:
            result = await _daemon_session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            # Daemon died, fall back to spawning new server
            await _stop_daemon()

    # Spawn new MCP server process
    server_params = StdioServerParameters(
        command=DEFAULT_SERVER_CMD, args=_build_server_args()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result
    except Exception as e:
        raise RuntimeError(
            f"DOMShell MCP call failed: {e}\n"
            f"Ensure Chrome is running with DOMShell extension installed.\n"
            f"Chrome Web Store: https://chromewebstore.google.com/detail/domshell"
        ) from e


async def _start_daemon() -> bool:
    """Start persistent daemon mode.

    Returns:
        True if daemon started successfully

    Raises:
        RuntimeError: If daemon fails to start
    """
    global _daemon_session, _daemon_read, _daemon_write, _daemon_client_context

    if _daemon_session is not None:
        return True  # Already running

    server_params = StdioServerParameters(
        command=DEFAULT_SERVER_CMD, args=_build_server_args()
    )

    try:
        # Store the context manager so we can properly clean it up later
        _daemon_client_context = stdio_client(server_params)
        _daemon_read, _daemon_write = await _daemon_client_context.__aenter__()
        _daemon_session = ClientSession(_daemon_read, _daemon_write)
        await _daemon_session.__aenter__()
        await _daemon_session.initialize()
        return True
    except Exception as e:
        _daemon_session = None
        _daemon_read = None
        _daemon_write = None
        _daemon_client_context = None
        raise RuntimeError(f"Failed to start DOMShell daemon: {e}") from e


def daemon_started() -> bool:
    """Check if daemon mode is active."""
    return _daemon_session is not None


def ls(path: str = "/", use_daemon: bool = False) -> dict:
    """List directory contents in the accessibility tree.

    Args:
        path: Path in accessibility tree (e.g., "/", "/main", "/main/div[0]")
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with 'entries' key containing list of accessible elements

    Example:
        >>> ls("/")
        {"path": "/", "entries": [{"name": "main", "role": "landmark", ...}]}
    """
    result = asyncio.run(_call_tool("domshell_ls", {"options": path}, use_daemon))
    return result
