# ruff: noqa: F403, F405, E501
from .domshell_backend_base import *  # noqa: F403

# fmt: off
from .domshell_backend_p2 import _call_tool  # noqa: E402,E501
# fmt: on


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
    result = asyncio.run(_call_tool("domshell_grep", {"pattern": pattern}, use_daemon))
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
