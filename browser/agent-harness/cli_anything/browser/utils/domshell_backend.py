"""DOMShell MCP client wrapper with DNS-pinned managed browser egress.

The browser is never attached to an arbitrary user Chrome process. The managed
runtime starts a private Chrome profile, pins ordinary browser connections
through a loopback egress proxy, and only then connects the pinned DOMShell
MCP server. This removes the DNS-rebinding gap between URL preflight and
Chrome's later DNS lookup.
"""

import asyncio
import os
from typing import Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from cli_anything.browser.utils import managed_domshell
from cli_anything.browser.utils import domshell_runtime

def _build_server_command() -> list[str]:
    """Start or reuse the managed runtime and build the private MCP bridge."""
    port, token = managed_domshell.ensure_managed_domshell()
    return domshell_runtime.command(
        "domshell-proxy",
        "--port", str(port),
        "--token", token,
    )


def _server_parameters() -> StdioServerParameters:
    """Create a minimal subprocess environment for the pinned MCP bridge."""

    command = _build_server_command()
    return StdioServerParameters(
        command=command[0],
        args=command[1:],
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.path.expanduser("~"),
            "npm_config_ignore_scripts": "true",
        },
    )

# Daemon mode: persistent MCP connection
_daemon_session: Optional[ClientSession] = None
_daemon_read: Optional[Any] = None
_daemon_write: Optional[Any] = None
_daemon_client_context: Optional[Any] = None  # Store stdio_client context manager


def is_available() -> tuple[bool, str]:
    """Prove that the managed DOMShell runtime can be started securely.

    Returns:
        (available, message): Tuple of availability status and descriptive message.

    Examples:
        >>> is_available()
        (True, "Managed DOMShell secure runtime is available")
        >>> is_available()
        (False, "DOMShell runtime is not installed")
    """
    runtime_status = domshell_runtime.status()
    if not runtime_status["installed"]:
        return (
            False,
            f"{runtime_status['reason']} Run `cli-anything-browser secure install` first."
        )

    try:
        managed_domshell.ensure_managed_domshell()
        return True, "Managed DOMShell secure runtime is available"
    except (managed_domshell.ManagedDOMShellError, RuntimeError) as error:
        return False, str(error)


def install_secure_runtime() -> dict[str, object]:
    """Install the lockfile-pinned local DOMShell runtime."""

    installed = domshell_runtime.install()
    return {"installed": True, "runtime": str(installed), "version": domshell_runtime.PACKAGE_VERSION}


async def _call_tool(
    tool_name: str,
    arguments: dict,
    use_daemon: bool = False
) -> Any:
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
        except Exception:
            # Daemon died, fall back to spawning new server
            await _stop_daemon()

    # Spawn new MCP server process
    server_params = _server_parameters()

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result
    except Exception as e:
        raise RuntimeError(
            f"DOMShell MCP call failed: {e}\n"
            "Run `cli-anything-browser secure status` and configure the locally "
            "built DOMShell extension for the managed browser."
        ) from e

# NOTE: Known limitation - Daemon mode uses asyncio.run() per tool call (in sync wrappers).
# Each asyncio.run() creates a new event loop. Async IO objects created in one loop
# (like the daemon session) may have issues when accessed from subsequent calls that
# create new loops. This is a documented limitation for v1; future work should use
# a single long-lived event loop (e.g., background thread + run_coroutine_threadsafe).
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

    server_params = _server_parameters()

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


async def _stop_daemon() -> None:
    """Stop persistent daemon mode."""
    global _daemon_session, _daemon_read, _daemon_write, _daemon_client_context

    if _daemon_session is None:
        return

    try:
        await _daemon_session.__aexit__(None, None, None)
        if _daemon_client_context:
            await _daemon_client_context.__aexit__(None, None, None)
    except Exception:
        pass  # Ignore cleanup errors
    finally:
        _daemon_session = None
        _daemon_read = None
        _daemon_write = None
        _daemon_client_context = None


def daemon_started() -> bool:
    """Check if daemon mode is active."""
    return _daemon_session is not None


# ── Sync wrappers for each DOMShell tool ─────────────────────────────

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


def cd(path: str, use_daemon: bool = False) -> dict:
    """Change directory in the accessibility tree.

    Args:
        path: Target path
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with 'path' key confirming current location

    Example:
        >>> cd("/main/div[0]")
        {"path": "/main/div[0]", "element": {...}}
    """
    result = asyncio.run(_call_tool("domshell_cd", {"path": path}, use_daemon))
    return result


def cat(path: str, use_daemon: bool = False) -> dict:
    """Read element content from the accessibility tree.

    Args:
        path: Path to element
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with element details including text, role, attributes

    Example:
        >>> cat("/main/button[0]")
        {"name": "Submit", "role": "button", "text": "Submit", ...}
    """
    result = asyncio.run(_call_tool("domshell_cat", {"name": path}, use_daemon))
    return result


def grep(pattern: str, use_daemon: bool = False) -> dict:
    """Search for pattern in accessibility tree.

    Searches from the current working directory.

    Args:
        pattern: Text pattern to search for
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with 'matches' key containing list of matching elements

    Example:
        >>> grep("Login")
        {"matches": ["/main/button[0]", "/main/link[1]"]}
    """
    result = asyncio.run(_call_tool(
        "domshell_grep",
        {"pattern": pattern},
        use_daemon
    ))
    return result


def click(path: str, use_daemon: bool = False) -> dict:
    """Click an element in the accessibility tree.

    Args:
        path: Path to element to click
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with action result

    Example:
        >>> click("/main/button[0]")
        {"action": "click", "path": "/main/button[0]", "status": "success"}
    """
    result = asyncio.run(_call_tool("domshell_click", {"name": path}, use_daemon))
    return result


def open_url(url: str, use_daemon: bool = False) -> dict:
    """Navigate to a URL in Chrome.

    Args:
        url: URL to navigate to
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with navigation result

    Example:
        >>> open_url("https://example.com")
        {"url": "https://example.com", "status": "loaded"}
    """
    result = asyncio.run(_call_tool("domshell_open", {"url": url}, use_daemon))
    return result


def reload(use_daemon: bool = False) -> dict:
    """Reload the current page.

    Args:
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with reload result
    """
    result = asyncio.run(_call_tool("domshell_reload", {}, use_daemon))
    return result


def back(use_daemon: bool = False) -> dict:
    """Navigate back in history.

    Args:
        use_daemon: Use persistent daemon connection if available

    Returns:
        Dict with navigation result
    """
    result = asyncio.run(_call_tool("domshell_back", {}, use_daemon))
    return result


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

        server_params = _server_parameters()
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await session.call_tool("domshell_focus", {"name": path})
                return await session.call_tool("domshell_type", {"text": text})

    return asyncio.run(_focus_and_type())


# ── Daemon control functions ───────────────────────────────────────────

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


def secure_runtime_status() -> dict[str, object]:
    """Expose only non-secret managed-runtime state to CLI users."""

    return managed_domshell.managed_status()


def stop_secure_runtime() -> None:
    """Stop the managed browser, MCP server, and DNS-pinning proxy."""

    managed_domshell.stop_managed_domshell()
