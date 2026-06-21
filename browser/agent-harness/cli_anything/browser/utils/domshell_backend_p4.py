# ruff: noqa: F403, F405, E501
from .domshell_backend_base import *  # noqa: F403

# fmt: off
from .domshell_backend_p1 import _build_server_args, _daemon_session, _stop_daemon  # noqa: E402,E501
from .domshell_backend_p2 import _call_tool, _start_daemon  # noqa: E402,E501
# fmt: on


def forward(use_daemon: bool = False) -> dict:
    """Navigate forward in history.

    Args:
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with navigation result
    """
    result = asyncio.run(_call_tool("domshell_forward", {}, use_daemon))
    return result


def type_text(path: str, text: str, use_daemon: bool = False) -> dict:
    """Type text into an input element.

    Focuses the element first (via domshell_focus), then types. Both operations
    run in a single MCP session so that focus state is preserved.

    Args:
        path: Path to input element
        text: Text to type
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with action result
    """

    async def _focus_and_type():
        global _daemon_session
        if use_daemon and _daemon_session is not None:
            await _daemon_session.call_tool("domshell_focus", {"name": path})
            return await _daemon_session.call_tool("domshell_type", {"text": text})

        server_params = StdioServerParameters(
            command=DEFAULT_SERVER_CMD, args=_build_server_args()
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await session.call_tool("domshell_focus", {"name": path})
                return await session.call_tool("domshell_type", {"text": text})

    return asyncio.run(_focus_and_type())


def start_daemon() -> bool:
    """Start persistent daemon mode (sync wrapper).

    Returns:
        True if daemon started successfully

    Raises:
        RuntimeError: If daemon fails to start
    """
    return asyncio.run(_start_daemon())


def stop_daemon() -> None:
    """Stop persistent daemon mode (sync wrapper)."""
    asyncio.run(_stop_daemon())
